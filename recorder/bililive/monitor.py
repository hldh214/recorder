from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from types import MappingProxyType
from typing import Callable, Mapping
from uuid import uuid4

from recorder.bililive.journal import JsonlJournal, baseline_fingerprint
from recorder.bililive.models import JournalReplay, RoomState, SessionState


POLL_INTERVAL_SECONDS = 60
QUIET_PERIOD_SECONDS = 30 * 60
LIVE_SEGMENT_QUIET_PERIOD_SECONDS = QUIET_PERIOD_SECONDS


Snapshot = Mapping[str, tuple[int, int]]


@dataclass(frozen=True)
class MonitorDecision:
    state: SessionState
    session_id: str | None = None
    baseline_paths: tuple[str, ...] = ()
    ready_paths: tuple[str, ...] = ()
    session_paths: tuple[str, ...] = ()
    snapshot: Mapping[str, tuple[int, int]] = field(default_factory=dict)
    quiet_since: datetime | None = None
    started_at: datetime | None = None
    reason: str = ''

    def __post_init__(self):
        object.__setattr__(
            self,
            'snapshot',
            MappingProxyType({
                path: tuple(identity)
                for path, identity in self.snapshot.items()
            }),
        )


def _default_id_factory():
    return str(uuid4())


def _parse_instant(value):
    if value is None:
        return None
    normalized = value[:-1] + '+00:00' if value.endswith(('Z', 'z')) else value
    instant = datetime.fromisoformat(normalized)
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError('restored session timestamps must be timezone-aware')
    return instant


def _normalize_snapshot(snapshot):
    normalized = {}
    for path, identity in snapshot.items():
        if not isinstance(path, str) or not path:
            raise TypeError('snapshot paths must be non-empty strings')
        if not isinstance(identity, (tuple, list)) or len(identity) != 2:
            raise TypeError('snapshot identities must contain size and mtime_ns')
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in identity
        ):
            raise TypeError(
                'snapshot size and mtime_ns must be non-negative integers'
            )
        normalized[path] = tuple(identity)
    return normalized


def _changed_paths(previous, current):
    return {
        path
        for path, identity in current.items()
        if previous.get(path) != identity
    }


def _manifest_snapshot(flv_paths, snapshot):
    frozen = {}
    for flv_path in flv_paths:
        identity = snapshot.get(flv_path)
        if identity is None:
            raise ValueError(
                f'settled snapshot is missing ready FLV {flv_path}'
            )
        frozen[flv_path] = identity
        xml_path = str(Path(flv_path).with_suffix('.xml'))
        xml_identity = snapshot.get(xml_path)
        if xml_identity is not None:
            frozen[xml_path] = xml_identity
    return frozen


def _validate_room_ownership(replay, room_id):
    if replay.session.room_id not in (None, room_id):
        raise ValueError('journal session has conflicting room_id')
    if any(manifest.room_id != room_id for manifest in replay.manifests):
        raise ValueError('journal manifest has conflicting room_id')


class SessionMonitorState:
    def __init__(self, initialized=False, id_factory=None):
        self.initialized = bool(initialized)
        self.id_factory = id_factory or _default_id_factory
        self.state = (
            SessionState.WAITING if self.initialized else SessionState.BASELINING
        )
        self.session_id = None
        self.session_paths = set()
        self.snapshot = {}
        self.quiet_since = None
        self.started_at = None
        self._restart_quiet_pending = False
        self._last_observed_at = None

    @classmethod
    def restore(cls, replay: JournalReplay, id_factory=None, room_id=None):
        if room_id is not None:
            _validate_room_ownership(replay, room_id)
        machine = cls(initialized=replay.initialized, id_factory=id_factory)
        session = replay.session
        if not isinstance(session.state, SessionState):
            raise ValueError('restored session state must be a SessionState')
        machine.state = session.state
        machine.session_id = session.session_id
        machine.session_paths = set(session.session_paths)
        machine.snapshot = dict(session.snapshot)
        machine.quiet_since = _parse_instant(session.quiet_since)
        machine.started_at = _parse_instant(session.started_at)
        machine._validate_restored_session(replay)
        observed_times = [
            instant
            for instant in (machine.started_at, machine.quiet_since)
            if instant is not None
        ]
        machine._last_observed_at = max(observed_times, default=None)

        if (
            not replay.initialized
            and session.state is not SessionState.SKIP_CURRENT_SESSION
        ):
            return cls(initialized=False, id_factory=machine.id_factory)
        if replay.initialized and session.state is SessionState.BASELINING:
            return cls(initialized=True, id_factory=machine.id_factory)
        if session.state is SessionState.READY:
            machine.state = SessionState.SETTLING
        matching_manifest = next((
            manifest
            for manifest in replay.manifests
            if manifest.manifest_id == machine.session_id
        ), None)
        if matching_manifest is not None:
            if session.state not in {
                SessionState.SETTLING,
                SessionState.READY,
            }:
                raise ValueError(
                    'matching session manifest has an invalid recovery state'
                )
            if room_id is not None and matching_manifest.room_id != room_id:
                raise ValueError(
                    'matching session manifest has conflicting room_id'
                )
            settled_at = _parse_instant(matching_manifest.settled_at)
            minimum_settled_at = machine.quiet_since + timedelta(
                seconds=QUIET_PERIOD_SECONDS
            )
            if settled_at < minimum_settled_at:
                raise ValueError(
                    'matching session manifest precedes the full quiet period'
                )
            expected_flv_paths = tuple(sorted(
                path
                for path in session.session_paths
                if path.lower().endswith('.flv')
            ))
            if matching_manifest.flv_paths != expected_flv_paths:
                raise ValueError(
                    'matching session manifest has conflicting flv_paths'
                )
            expected_snapshot = _manifest_snapshot(
                expected_flv_paths, session.snapshot
            )
            if dict(matching_manifest.snapshot) != expected_snapshot:
                raise ValueError(
                    'matching session manifest has conflicting snapshot'
                )
            manifest_started_at = _parse_instant(
                matching_manifest.started_at
            )
            if manifest_started_at != machine.started_at:
                raise ValueError(
                    'matching session manifest has conflicting started_at'
                )
            if (
                machine._last_observed_at is None
                or settled_at > machine._last_observed_at
            ):
                machine._last_observed_at = settled_at
            machine.state = SessionState.WAITING
            machine.session_id = None
            machine.session_paths.clear()
            machine.quiet_since = None
            machine.started_at = None
            return machine
        machine._restart_quiet_pending = machine.state in {
            SessionState.RECORDING,
            SessionState.SETTLING,
            SessionState.SKIP_CURRENT_SESSION,
        }
        return machine

    def observe(self, now: datetime, room: RoomState | None, snapshot: Snapshot):
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError('now must be timezone-aware')
        if self._last_observed_at is not None and now < self._last_observed_at:
            raise ValueError('observation time cannot be earlier than prior state')
        current = _normalize_snapshot(snapshot)

        if room is None:
            self._last_observed_at = now
            if self.state in {
                SessionState.SKIP_CURRENT_SESSION,
                SessionState.RECORDING,
                SessionState.SETTLING,
                SessionState.READY,
            }:
                self._restart_quiet_pending = True
            return self._decision(reason='room state unavailable')
        if not isinstance(room, RoomState):
            raise TypeError('room must be RoomState or None')
        self._last_observed_at = now

        if self.state is SessionState.BASELINING:
            return self._observe_first(now, room, current)
        if self.state is SessionState.WAITING:
            return self._observe_waiting(now, room, current)
        if self.state is SessionState.SKIP_CURRENT_SESSION:
            return self._observe_skipped(now, room, current)
        if self.state is SessionState.RECORDING:
            return self._observe_recording(now, room, current)
        if self.state is SessionState.SETTLING:
            return self._observe_settling(now, room, current)
        if self.state is SessionState.READY:
            return self._observe_ready(now, room, current)
        return self._decision(reason='publication in progress')

    def rearm(self):
        if self.state is not SessionState.READY:
            raise RuntimeError('only a ready session can be rearmed')
        self.state = SessionState.WAITING
        self.session_id = None
        self.session_paths.clear()
        self.quiet_since = None
        self.started_at = None
        self._restart_quiet_pending = False

    def persistent_signature(self):
        return (
            self.state,
            self.session_id,
            tuple(sorted(self.session_paths)),
            tuple(sorted(self.snapshot.items())),
            self.quiet_since,
            self.started_at,
        )

    def _validate_restored_session(self, replay):
        state = self.state
        active_states = {
            SessionState.SKIP_CURRENT_SESSION,
            SessionState.RECORDING,
            SessionState.SETTLING,
            SessionState.READY,
        }
        if state in active_states:
            if not isinstance(self.session_id, str) or not self.session_id:
                raise ValueError('active session state requires a session_id')
            if self.started_at is None:
                raise ValueError('active session state requires started_at')
            if self.quiet_since is None:
                raise ValueError('active session state requires quiet_since')
            if self.quiet_since < self.started_at:
                raise ValueError(
                    'active session state quiet_since cannot precede started_at'
                )
            if (
                state is SessionState.SKIP_CURRENT_SESSION
                and replay.initialized
            ):
                raise ValueError(
                    'skip-current-session state cannot already be initialized'
                )
            if (
                state is not SessionState.SKIP_CURRENT_SESSION
                and not replay.initialized
            ):
                raise ValueError(
                    'active session state requires initialized journal'
                )
            return

        if state in {SessionState.WAITING, SessionState.BASELINING}:
            if any((
                self.session_id is not None,
                bool(self.session_paths),
                self.quiet_since is not None,
                self.started_at is not None,
            )):
                raise ValueError('idle session state contains stale session state')
            return

        raise ValueError(f'unsupported restored session state: {state.value}')

    def _observe_first(self, now, room, current):
        self.snapshot = current
        if not room.active:
            self.initialized = True
            self.state = SessionState.WAITING
            return self._decision(baseline_paths=tuple(sorted(current)))

        self.state = SessionState.SKIP_CURRENT_SESSION
        self.session_id = self.id_factory()
        self.session_paths = set(current)
        self.quiet_since = now
        self.started_at = now
        return self._decision(baseline_paths=tuple(sorted(self.session_paths)))

    def _observe_waiting(self, now, room, current):
        previous = self.snapshot
        self.snapshot = current
        if not room.active:
            return self._decision()

        self.state = SessionState.RECORDING
        self.session_id = self.id_factory()
        self.session_paths = _changed_paths(previous, current)
        self.quiet_since = now
        self.started_at = now
        return self._decision()

    def _observe_skipped(self, now, room, current):
        changed = current != self.snapshot
        self.session_paths.update(_changed_paths(self.snapshot, current))
        self.snapshot = current
        if changed or self.quiet_since is None or self._restart_quiet_pending:
            self.quiet_since = now
        self._restart_quiet_pending = False

        baseline_paths = tuple(sorted(self.session_paths))
        if room.active:
            return self._decision(baseline_paths=baseline_paths)
        if now - self.quiet_since < timedelta(seconds=QUIET_PERIOD_SECONDS):
            return self._decision(baseline_paths=baseline_paths)

        self.initialized = True
        self.state = SessionState.WAITING
        self.session_id = None
        self.session_paths.clear()
        self.quiet_since = None
        self.started_at = None
        return self._decision(baseline_paths=baseline_paths)

    def _observe_recording(self, now, room, current):
        changed = current != self.snapshot
        self.session_paths.update(_changed_paths(self.snapshot, current))
        self.snapshot = current
        if changed or self.quiet_since is None or self._restart_quiet_pending:
            self.quiet_since = now
        self._restart_quiet_pending = False

        if room.active:
            return self._decision()
        self.quiet_since = now
        self.state = SessionState.SETTLING
        return self._decision()

    def _observe_settling(self, now, room, current):
        changed = current != self.snapshot
        self.session_paths.update(_changed_paths(self.snapshot, current))
        self.snapshot = current
        if changed or self.quiet_since is None or self._restart_quiet_pending:
            self.quiet_since = now
        self._restart_quiet_pending = False

        if room.active:
            self.state = SessionState.RECORDING
            return self._decision()
        if now - self.quiet_since < timedelta(seconds=QUIET_PERIOD_SECONDS):
            return self._decision()

        self.state = SessionState.READY
        return self._decision(
            ready_paths=tuple(
                sorted(
                    path for path in self.session_paths
                    if path.lower().endswith('.flv')
                )
            )
        )

    def _observe_ready(self, now, room, current):
        changed = current != self.snapshot
        self.session_paths.update(_changed_paths(self.snapshot, current))
        self.snapshot = current
        if self._restart_quiet_pending:
            self._restart_quiet_pending = False
            self.quiet_since = now
            self.state = (
                SessionState.RECORDING
                if room.active else SessionState.SETTLING
            )
            return self._decision()
        if room.active:
            self.state = SessionState.RECORDING
            if changed:
                self.quiet_since = now
            return self._decision()
        if changed:
            self.state = SessionState.SETTLING
            self.quiet_since = now
            return self._decision()
        return self._decision(
            ready_paths=tuple(
                sorted(
                    path for path in self.session_paths
                    if path.lower().endswith('.flv')
                )
            )
        )

    def _decision(self, baseline_paths=(), ready_paths=(), reason=''):
        return MonitorDecision(
            state=self.state,
            session_id=self.session_id,
            baseline_paths=tuple(baseline_paths),
            ready_paths=tuple(ready_paths),
            session_paths=tuple(sorted(self.session_paths)),
            snapshot=dict(self.snapshot),
            quiet_since=self.quiet_since,
            started_at=self.started_at,
            reason=reason,
        )


class BililiveSessionMonitor:
    def __init__(
        self,
        journal: JsonlJournal,
        room_id: int,
        machine: SessionMonitorState | None = None,
        id_factory: Callable[[], str] | None = None,
        live_segment_manifests=False,
    ):
        if isinstance(room_id, bool) or not isinstance(room_id, int):
            raise TypeError('room_id must be an integer')
        if not isinstance(live_segment_manifests, bool):
            raise TypeError('live_segment_manifests must be a boolean')
        self.journal = journal
        self.room_id = room_id
        self.live_segment_manifests = live_segment_manifests
        replay = journal.replay()
        _validate_room_ownership(replay, room_id)
        self.machine = machine or SessionMonitorState.restore(
            replay, id_factory=id_factory, room_id=room_id
        )

    def observe(self, now: datetime, room: RoomState | None, snapshot: Snapshot):
        was_initialized = self.machine.initialized
        previous_state = self.machine.state
        previous = self.machine.persistent_signature()

        try:
            if self.machine.state is SessionState.WAITING and room is not None:
                if not isinstance(room, RoomState):
                    raise TypeError('room must be RoomState or None')
                replay = self.journal.replay()
                if replay.pending_resettles:
                    return self._claim_pending_resettle(
                        now, room, snapshot, replay
                    )
            decision = self.machine.observe(now, room, snapshot)
            if not was_initialized and self.machine.initialized:
                if previous_state is SessionState.BASELINING:
                    self._append_baselining_ownership(decision)
                self._append_baselines(decision)
                self._append_session_state()
                self.journal.append('initialized')
                return decision

            if decision.state is SessionState.READY:
                ready_paths = self._unmanifested_flv_paths(
                    decision.ready_paths
                )
                if not ready_paths:
                    self.machine.rearm()
                    self._append_session_state()
                    return decision
                self.journal.append(
                    'session_manifest_ready',
                    manifest_id=decision.session_id,
                    room_id=self.room_id,
                    started_at=decision.started_at.isoformat(),
                    settled_at=now.isoformat(),
                    flv_paths=ready_paths,
                    snapshot=_manifest_snapshot(
                        ready_paths, decision.snapshot
                    ),
                )
                self.machine.rearm()
                self._append_session_state()
                return decision

            if room is not None and room.active:
                self._append_live_segment_manifests(now, decision)

            if previous != self.machine.persistent_signature():
                self._append_session_state()
            return decision
        except Exception:
            id_factory = self.machine.id_factory
            try:
                self.machine = SessionMonitorState.restore(
                    self.journal.replay(),
                    id_factory=id_factory,
                    room_id=self.room_id,
                )
            except Exception:
                self.machine = SessionMonitorState(
                    initialized=False, id_factory=id_factory
                )
            raise

    def _append_live_segment_manifests(self, now, decision):
        if (
            not self.live_segment_manifests
            or decision.state is not SessionState.RECORDING
            or decision.started_at is None
        ):
            return
        for path in self._live_ready_paths(now, decision):
            self.journal.append(
                'session_manifest_ready',
                manifest_id=self.machine.id_factory(),
                room_id=self.room_id,
                started_at=decision.started_at.isoformat(),
                settled_at=now.isoformat(),
                flv_paths=(path,),
                snapshot=_manifest_snapshot((path,), decision.snapshot),
            )

    def _live_ready_paths(self, now, decision):
        candidates = tuple(
            path for path in self._unmanifested_flv_paths(
                decision.session_paths
            )
            if path in decision.snapshot
        )
        if len(candidates) < 2:
            return ()
        current = decision.snapshot
        latest = max(candidates, key=lambda path: (current[path][1], path))
        cutoff_ns = int(
            (now - timedelta(seconds=LIVE_SEGMENT_QUIET_PERIOD_SECONDS))
            .timestamp() * 1_000_000_000
        )
        return tuple(
            path for path in candidates
            if path != latest and current[path][1] <= cutoff_ns
        )

    def _unmanifested_flv_paths(self, paths):
        claimed = {
            path
            for manifest in self.journal.replay().manifests
            if not manifest.invalidated
            for path in manifest.flv_paths
        }
        return tuple(sorted(
            path for path in paths
            if path.lower().endswith('.flv') and path not in claimed
        ))

    def _claim_pending_resettle(self, now, room, snapshot, replay):
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError('now must be timezone-aware')
        if (
            self.machine._last_observed_at is not None
            and now < self.machine._last_observed_at
        ):
            raise ValueError('observation time cannot be earlier than prior state')
        request = replay.pending_resettles[0]
        source = next(
            manifest for manifest in replay.manifests
            if manifest.manifest_id == request.source_manifest_id
        )
        current = _normalize_snapshot(snapshot)
        missing_flvs = [
            path for path in source.flv_paths if path not in current
        ]
        if missing_flvs:
            if self._can_discard_deleted_published_resettle(
                source, missing_flvs, replay
            ):
                self.journal.append(
                    'session_resettle_discarded',
                    source_manifest_id=source.manifest_id,
                    reason=(
                        'all source FLVs were durably deleted after '
                        'successful publication'
                    ),
                )
                return self.observe(now, room, current)
            raise ValueError(
                'pending resettle current source FLV is missing: '
                + ', '.join(missing_flvs)
            )
        if not source.flv_paths:
            raise ValueError('pending resettle has no current source FLV')
        session_paths = set(source.flv_paths)
        for flv_path in source.flv_paths:
            xml_path = str(Path(flv_path).with_suffix('.xml'))
            if xml_path in current:
                session_paths.add(xml_path)
        if room.active:
            session_paths.update(
                path for path, identity in current.items()
                if path.lower().endswith(('.flv', '.xml'))
                and replay.session.snapshot.get(path) != identity
            )
        replacement_id = self.machine.id_factory()
        state = (
            SessionState.RECORDING
            if room.active else SessionState.SETTLING
        )
        started_at = _parse_instant(source.started_at)
        self.journal.append(
            'session_resettle_started',
            source_manifest_id=source.manifest_id,
            replacement_manifest_id=replacement_id,
            room_id=self.room_id,
            state=state.value,
            session_paths=tuple(sorted(session_paths)),
            snapshot=current,
            quiet_since=now.isoformat(),
            started_at=source.started_at,
        )

        self.machine.state = state
        self.machine.session_id = replacement_id
        self.machine.session_paths = session_paths
        self.machine.snapshot = current
        self.machine.quiet_since = now
        self.machine.started_at = started_at
        self.machine._restart_quiet_pending = False
        self.machine._last_observed_at = now
        return self.machine._decision(reason='claimed pending resettle')

    @staticmethod
    def _can_discard_deleted_published_resettle(source, missing_flvs, replay):
        if len(missing_flvs) != len(source.flv_paths):
            return False
        for path in source.flv_paths:
            matches = tuple(
                state for state in replay.files.values()
                if state.manifest_id == source.manifest_id and state.file == path
            )
            if len(matches) != 1:
                return False
            state = matches[0]
            if (
                path not in state.deleted_paths
                or not state.video_id
                or not state.youtube_processed
                or not (
                    state.caption_uploaded
                    or state.caption_status == 'not_requested'
                )
            ):
                return False
        return True

    def _append_baselining_ownership(self, decision):
        self.journal.append(
            'session_state',
            room_id=self.room_id,
            state=SessionState.BASELINING.value,
            session_id=None,
            session_paths=(),
            snapshot=dict(decision.snapshot),
            quiet_since=None,
            started_at=None,
        )

    def _append_baselines(self, decision):
        for path in decision.baseline_paths:
            identity = decision.snapshot.get(path)
            if identity is None:
                continue
            self.journal.append(
                'baseline',
                fingerprint=baseline_fingerprint(path, *identity),
                file=path,
                source_size=identity[0],
                source_mtime_ns=identity[1],
            )

    def _append_session_state(self):
        self.journal.append(
            'session_state',
            room_id=self.room_id,
            state=self.machine.state.value,
            session_id=self.machine.session_id,
            session_paths=tuple(sorted(self.machine.session_paths)),
            snapshot=dict(self.machine.snapshot),
            quiet_since=(
                self.machine.quiet_since.isoformat()
                if self.machine.quiet_since is not None else None
            ),
            started_at=(
                self.machine.started_at.isoformat()
                if self.machine.started_at is not None else None
            ),
        )

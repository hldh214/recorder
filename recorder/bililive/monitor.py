from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable, Mapping
from uuid import uuid4

from recorder.bililive.journal import JsonlJournal, baseline_fingerprint
from recorder.bililive.models import JournalReplay, RoomState, SessionState


POLL_INTERVAL_SECONDS = 60
QUIET_PERIOD_SECONDS = 30 * 60


Snapshot = Mapping[str, tuple[int, int]]


@dataclass(frozen=True)
class MonitorDecision:
    state: SessionState
    session_id: str | None = None
    baseline_paths: tuple[str, ...] = ()
    ready_paths: tuple[str, ...] = ()
    session_paths: tuple[str, ...] = ()
    snapshot: dict[str, tuple[int, int]] = field(default_factory=dict)
    quiet_since: datetime | None = None
    started_at: datetime | None = None
    reason: str = ''


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

    @classmethod
    def restore(cls, replay: JournalReplay, id_factory=None):
        machine = cls(initialized=replay.initialized, id_factory=id_factory)
        session = replay.session

        if not replay.initialized:
            if session.state is not SessionState.SKIP_CURRENT_SESSION:
                return machine
        elif session.state not in {
            SessionState.WAITING,
            SessionState.RECORDING,
            SessionState.SETTLING,
            SessionState.READY,
        }:
            return machine

        machine.state = session.state
        if session.state is SessionState.READY:
            machine.state = SessionState.SETTLING
        machine.session_id = session.session_id
        machine.session_paths = set(session.session_paths)
        machine.snapshot = dict(session.snapshot)
        machine.quiet_since = _parse_instant(session.quiet_since)
        machine.started_at = _parse_instant(session.started_at)
        if any(
            manifest.manifest_id == machine.session_id
            for manifest in replay.manifests
        ):
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
        current = _normalize_snapshot(snapshot)

        if room is None:
            return self._decision(reason='room state unavailable')
        if not isinstance(room, RoomState):
            raise TypeError('room must be RoomState or None')

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
    ):
        if isinstance(room_id, bool) or not isinstance(room_id, int):
            raise TypeError('room_id must be an integer')
        self.journal = journal
        self.room_id = room_id
        self.machine = machine or SessionMonitorState.restore(
            journal.replay(), id_factory=id_factory
        )

    def observe(self, now: datetime, room: RoomState | None, snapshot: Snapshot):
        was_initialized = self.machine.initialized
        previous = self.machine.persistent_signature()
        decision = self.machine.observe(now, room, snapshot)

        try:
            if not was_initialized and self.machine.initialized:
                self._append_baselines(decision)
                self._append_session_state()
                self.journal.append('initialized')
                return decision

            if decision.state is SessionState.READY:
                self.journal.append(
                    'session_manifest_ready',
                    manifest_id=decision.session_id,
                    room_id=self.room_id,
                    started_at=decision.started_at.isoformat(),
                    settled_at=now.isoformat(),
                    flv_paths=decision.ready_paths,
                )
                self.machine.rearm()
                self._append_session_state()
                return decision

            if previous != self.machine.persistent_signature():
                self._append_session_state()
            return decision
        except Exception:
            id_factory = self.machine.id_factory
            try:
                self.machine = SessionMonitorState.restore(
                    self.journal.replay(), id_factory=id_factory
                )
            except Exception:
                self.machine = SessionMonitorState(
                    initialized=False, id_factory=id_factory
                )
            raise

    def _append_baselines(self, decision):
        for path in decision.baseline_paths:
            identity = decision.snapshot.get(path)
            if identity is None:
                continue
            self.journal.append(
                'baseline',
                fingerprint=baseline_fingerprint(path, *identity),
                file=path,
            )

    def _append_session_state(self):
        self.journal.append(
            'session_state',
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

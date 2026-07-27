import logging
import math
import os
import shutil
import stat
import uuid
from collections.abc import Mapping
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path

from recorder.bililive.models import (
    JournalDeleteIntent,
    JournalFileState,
    JournalManifest,
    JournalResettleRequest,
    JournalSessionState,
    SessionState,
)
from recorder.bililive.journal import baseline_fingerprint
from recorder.bililive.cleanup_fs import (
    QUARANTINE_DIRECTORY,
    RootDirectory,
    UnsafeCleanupPathError,
)


DISK_CLEANUP_THRESHOLD_PERCENT = 85


_IGNORED_EVENTS = frozenset({
    'ignored_invalid',
    'ignored_tiny',
    'ignored_invalid_tail',
})
_KNOWN_FILE_EVENTS = _IGNORED_EVENTS | frozenset({
    'baseline',
    'file_ready',
    'upload_started',
    'video_upload_rejected',
    'video_uploaded',
    'description_updated',
    'caption_status',
    'caption_source_frozen',
    'caption_uploaded',
    'playlist_inserted',
    'youtube_processed',
    'stage_retry_scheduled',
    'ambiguous',
    'fatal',
})
_TERMINAL_CAPTION_STATUSES = frozenset({'uploaded', 'existing'})
_HARD_VIDEO_EVENTS = frozenset({
    'file_ready',
    'upload_started',
    'video_upload_rejected',
    'video_uploaded',
    'ambiguous',
})
_ACTIVE_SESSION_STATES = frozenset({
    SessionState.SKIP_CURRENT_SESSION,
    SessionState.RECORDING,
    SessionState.SETTLING,
    SessionState.READY,
})
_DELETE_REASON = 'disk usage at or above 85 percent'


def filesystem_usage_percent(path):
    usage = shutil.disk_usage(path)
    return int(usage.used / usage.total * 100)


@dataclass(frozen=True)
class CleanupResult:
    deleted: tuple[Path, ...]
    protected: tuple[Path, ...]
    disk_usage_percent: int
    exhausted: bool


@dataclass(frozen=True)
class _Candidate:
    path: Path
    fingerprint: str
    mtime_ns: int
    identity: tuple[int, int, int, int]


class StateAwareCleanup:
    def __init__(self, journal, root, disk_usage=filesystem_usage_percent):
        self.journal = journal
        self.root = Path(root).resolve()
        self.disk_usage = disk_usage

    def run(self, states, dry_run):
        replay = self.journal.replay()
        reconciled_deleted = []
        reconciled_intents = []
        reconciliation_protected = set()
        control_graph_valid = self._control_graph_valid(replay)
        if replay.pending_deletions and not dry_run and control_graph_valid:
            with RootDirectory(self.root) as root_directory:
                for intent in replay.pending_deletions:
                    reconciled, protected = self._reconcile_intent(
                        root_directory, intent
                    )
                    if reconciled:
                        reconciled_deleted.append(Path(intent.original_path))
                        reconciled_intents.append(intent)
                    if protected:
                        reconciliation_protected.add(
                            Path(intent.original_path)
                        )
            replay = self._replay_after_reconciliation(
                replay, reconciled_intents
            )

        protected_by_control = (
            self._control_protected_paths(
                replay,
                {
                    item.manifest_id: item
                    for item in replay.manifests
                },
            )
            if control_graph_valid
            else self._all_replay_paths(replay)
        )

        usage = self.disk_usage(self.root)
        if usage < DISK_CLEANUP_THRESHOLD_PERCENT:
            return CleanupResult(
                tuple(reconciled_deleted),
                self._ordered(
                    reconciliation_protected | protected_by_control
                ),
                usage,
                False,
            )

        states = tuple(replay.files.values())

        manifest_groups = {}
        for item in replay.manifests:
            if self._non_empty_string(item.manifest_id):
                manifest_groups.setdefault(item.manifest_id, []).append(item)
        manifest_index = {
            manifest_id: items[0]
            for manifest_id, items in manifest_groups.items()
            if len(items) == 1
        }
        if control_graph_valid:
            protected_by_control = self._control_protected_paths(
                replay, manifest_index
            )
        assessments = {}
        owners = {}
        identities = {}

        for state in states:
            shape_valid = self._state_shape_valid(state)
            manifest = None
            relationship_valid = (
                shape_valid and self._state_binding_valid(state)
            )
            if shape_valid and state.manifest_id is not None:
                manifests = manifest_groups.get(state.manifest_id, ())
                if len(manifests) == 1:
                    manifest = manifests[0]
                    relationship_valid = (
                        relationship_valid
                        and self._manifest_binding_valid(manifest, state)
                    )
                else:
                    relationship_valid = False
            if (
                relationship_valid
                and manifest is not None
                and manifest.invalidated
            ):
                # An invalidated generation is either protected by its resettle
                # chain or superseded by a safely completed replacement.
                continue
            for path, eligible, is_xml in self._state_paths(
                state, relationship_valid
            ):
                if relationship_valid and str(path) in state.deleted_paths:
                    continue
                owners.setdefault(path, set()).add(state.fingerprint)
                safe, file_stat = self._safe_regular_file(path)
                frozen = self._matches_required_identity(
                    path,
                    file_stat,
                    manifest,
                    state,
                    is_xml=is_xml,
                )
                allowed = bool(eligible and safe and frozen)
                assessments.setdefault(path, []).append(allowed)
                if safe and file_stat is not None:
                    identities[path] = self._stat_identity(file_stat)

        protected = set(protected_by_control) | reconciliation_protected
        candidates = []
        for path, path_assessments in assessments.items():
            if (
                path in protected_by_control
                or not all(path_assessments)
                or len(owners[path]) != 1
            ):
                protected.add(path)
                continue
            file_stat = self._lstat(path)
            if file_stat is None:
                protected.add(path)
                continue
            candidates.append(_Candidate(
                path=path,
                fingerprint=next(iter(owners[path])),
                mtime_ns=file_stat.st_mtime_ns,
                identity=identities[path],
            ))
        candidates.sort(key=lambda item: (item.mtime_ns, str(item.path)))

        if dry_run:
            planned = tuple(item.path for item in candidates)
            exhausted = not planned
            if exhausted:
                self._log_exhausted(usage)
            return CleanupResult(
                planned, self._ordered(protected), usage, exhausted
            )

        deleted = list(reconciled_deleted)
        with RootDirectory(self.root) as root_directory:
            for candidate in candidates:
                if usage < DISK_CLEANUP_THRESHOLD_PERCENT:
                    break
                try:
                    current_stat = root_directory.lstat(candidate.path)
                    if (
                        current_stat is None
                        or current_stat.st_nlink != 1
                        or self._stat_identity(current_stat)
                        != candidate.identity
                    ):
                        protected.add(candidate.path)
                        continue
                    self._quarantine_candidate(root_directory, candidate)
                except (OSError, UnsafeCleanupPathError):
                    protected.add(candidate.path)
                    continue
                deleted.append(candidate.path)
                usage = self.disk_usage(self.root)

        exhausted = usage >= DISK_CLEANUP_THRESHOLD_PERCENT
        if exhausted:
            self._log_exhausted(usage)
        return CleanupResult(
            tuple(deleted), self._ordered(protected), usage, exhausted
        )

    def _quarantine_candidate(self, root_directory, candidate):
        quarantine_path = (
            f'{QUARANTINE_DIRECTORY}/{uuid.uuid4().hex}'
        )
        identity = candidate.identity
        root_directory.ensure_quarantine()
        self.journal.append(
            'source_delete_intent',
            fingerprint=candidate.fingerprint,
            original_path=str(candidate.path),
            quarantine_path=quarantine_path,
            dev=identity[0],
            ino=identity[1],
            size=identity[2],
            mtime_ns=identity[3],
            reason=_DELETE_REASON,
        )
        intent = JournalDeleteIntent(
            fingerprint=candidate.fingerprint,
            original_path=str(candidate.path),
            quarantine_path=quarantine_path,
            dev=identity[0],
            ino=identity[1],
            size=identity[2],
            mtime_ns=identity[3],
            reason=_DELETE_REASON,
        )
        root_directory.rename_to_quarantine(
            candidate.path, quarantine_path, identity
        )
        self._record_source_deleted(intent)
        root_directory.unlink_quarantine(quarantine_path, identity)
        self._record_quarantine_removed(intent)

    def _record_source_deleted(self, intent):
        self.journal.append(
            'source_deleted',
            fingerprint=intent.fingerprint,
            path=intent.original_path,
            reason=intent.reason,
        )

    def _record_quarantine_removed(self, intent):
        self.journal.append(
            'quarantine_removed',
            fingerprint=intent.fingerprint,
            original_path=intent.original_path,
            quarantine_path=intent.quarantine_path,
        )

    @staticmethod
    def _replay_after_reconciliation(replay, reconciled_intents):
        if not reconciled_intents:
            return replay
        files = dict(replay.files)
        for intent in reconciled_intents:
            state = files[intent.fingerprint]
            if intent.original_path not in state.deleted_paths:
                files[intent.fingerprint] = replace(
                    state,
                    deleted_paths=state.deleted_paths
                    + (intent.original_path,),
                )
        return replace(
            replay,
            files=files,
            pending_deletions=tuple(
                intent for intent in replay.pending_deletions
                if intent not in reconciled_intents
            ),
        )

    @staticmethod
    def _intent_identity(intent):
        return (intent.dev, intent.ino, intent.size, intent.mtime_ns)

    def _reconcile_intent(self, root_directory, intent):
        identity = self._intent_identity(intent)
        try:
            original_stat = root_directory.lstat(intent.original_path)
            quarantine_stat = root_directory.quarantine_stat(
                intent.quarantine_path
            )
        except (OSError, UnsafeCleanupPathError):
            return False, True
        original_matches = (
            original_stat is not None
            and original_stat.st_nlink == 1
            and self._stat_identity(original_stat) == identity
        )
        quarantine_matches = (
            quarantine_stat is not None
            and quarantine_stat.st_nlink == 1
            and self._stat_identity(quarantine_stat) == identity
        )
        if intent.source_deleted:
            if original_stat is not None:
                return False, True
            if quarantine_matches:
                root_directory.unlink_quarantine(
                    intent.quarantine_path, identity
                )
            elif quarantine_stat is not None:
                return False, True
            self._record_quarantine_removed(intent)
            return True, False

        if original_matches and quarantine_stat is None:
            root_directory.rename_to_quarantine(
                intent.original_path, intent.quarantine_path, identity
            )
        elif original_stat is not None or not quarantine_matches:
            return False, True
        self._record_source_deleted(intent)
        root_directory.unlink_quarantine(intent.quarantine_path, identity)
        self._record_quarantine_removed(intent)
        return True, False

    def _state_paths(self, state, relationship_valid):
        file_value = (
            state.file if self._non_empty_string(state.file) else None
        )
        xml_value = (
            state.xml_file
            if self._non_empty_string(state.xml_file)
            else None
        )
        if file_value is not None:
            video_path = self._lexical_absolute(file_value)
        elif xml_value is not None:
            video_path = self._lexical_absolute(xml_value).with_suffix('.flv')
        else:
            return
        derived_xml_path = video_path.with_suffix('.xml')
        claimed_xml_path = (
            self._lexical_absolute(xml_value)
            if xml_value is not None
            else None
        )
        standalone_xml_baseline = (
            relationship_valid
            and state.event == 'baseline'
            and claimed_xml_path is None
            and video_path.suffix.lower() == '.xml'
        )
        if standalone_xml_baseline:
            yield video_path, True, True
            return
        path_binding_valid = (
            video_path.suffix.lower() == '.flv'
            and (
                claimed_xml_path is None
                or claimed_xml_path == derived_xml_path
            )
        )
        if not relationship_valid or not path_binding_valid:
            protected_paths = {video_path, derived_xml_path}
            if claimed_xml_path is not None and not path_binding_valid:
                protected_paths.add(claimed_xml_path)
                protected_paths.add(claimed_xml_path.with_suffix('.flv'))
            for path in sorted(protected_paths, key=str):
                yield path, False, path.suffix.lower() == '.xml'
            return

        xml_path = claimed_xml_path or derived_xml_path
        eligibility_valid = relationship_valid and path_binding_valid
        baseline_or_ignored = eligibility_valid and (
            state.event == 'baseline' or state.event in _IGNORED_EVENTS
        )
        video_eligible = self._video_eligible(
            state, baseline_or_ignored, eligibility_valid
        )
        xml_eligible = self._xml_eligible(
            state, baseline_or_ignored, eligibility_valid
        )
        yield video_path, video_eligible, False
        if state.event == 'baseline' and claimed_xml_path is None:
            return
        if claimed_xml_path is None and not os.path.lexists(xml_path):
            return
        yield xml_path, xml_eligible, True

    @classmethod
    def _state_binding_valid(cls, state):
        video_path = cls._lexical_absolute(state.file)
        if (
            state.event == 'baseline'
            and state.xml_file is None
            and video_path.suffix.lower() == '.xml'
        ):
            return True
        if video_path.suffix.lower() != '.flv':
            return False
        if state.xml_file is None:
            return True
        return (
            cls._lexical_absolute(state.xml_file)
            == video_path.with_suffix('.xml')
        )

    @classmethod
    def _manifest_binding_valid(cls, manifest, state):
        if manifest.manifest_id != state.manifest_id:
            return False
        if not isinstance(manifest.flv_paths, (tuple, list)):
            return False

        flv_paths = []
        for raw_path in manifest.flv_paths:
            if not cls._non_empty_string(raw_path):
                return False
            path = cls._lexical_absolute(raw_path)
            if str(path) != raw_path or path.suffix.lower() != '.flv':
                return False
            flv_paths.append(path)
        if len(flv_paths) != len(set(flv_paths)):
            return False

        video_path = cls._lexical_absolute(state.file)
        if video_path not in flv_paths:
            return False
        if not isinstance(manifest.snapshot, Mapping):
            return False

        snapshot_paths = set()
        for raw_path, identity in manifest.snapshot.items():
            if not cls._non_empty_string(raw_path):
                return False
            path = cls._lexical_absolute(raw_path)
            if str(path) != raw_path or path in snapshot_paths:
                return False
            if (
                not isinstance(identity, (tuple, list))
                or len(identity) != 2
                or any(
                    not cls._non_negative_integer(value)
                    for value in identity
                )
            ):
                return False
            snapshot_paths.add(path)

        allowed_paths = set(flv_paths)
        allowed_paths.update(path.with_suffix('.xml') for path in flv_paths)
        return (
            set(flv_paths).issubset(snapshot_paths)
            and snapshot_paths.issubset(allowed_paths)
        )

    @staticmethod
    def _lexical_absolute(value):
        return Path(os.path.abspath(os.path.normpath(value)))

    @classmethod
    def _video_eligible(cls, state, baseline_or_ignored, shape_valid):
        if not shape_valid:
            return False
        if cls._inconsistent_lifecycle(state):
            return False
        if baseline_or_ignored:
            return True
        if state.youtube_processed is not True or not state.video_id:
            return False
        if state.event in _HARD_VIDEO_EVENTS:
            return False
        if state.event == 'stage_retry_scheduled':
            return state.stage != 'video'
        if state.event == 'fatal':
            return state.error_stage != 'video'
        return True

    @classmethod
    def _xml_eligible(cls, state, baseline_or_ignored, shape_valid):
        if not shape_valid:
            return False
        if cls._inconsistent_lifecycle(state):
            return False
        if baseline_or_ignored:
            return True
        if (
            state.caption_uploaded is not True
            or state.caption_refresh_required is True
            or not state.video_id
            or state.event in _HARD_VIDEO_EVENTS
        ):
            return False
        if state.event == 'caption_source_frozen':
            return False
        if (
            state.event == 'stage_retry_scheduled'
            and state.stage in {'video', 'caption'}
        ):
            return False
        if (
            state.event == 'fatal'
            and state.error_stage in {'video', 'caption'}
        ):
            return False
        return True

    @classmethod
    def _state_shape_valid(cls, state):
        if (
            not cls._non_empty_string(state.fingerprint)
            or not cls._non_empty_string(state.event)
            or not cls._non_empty_string(state.file)
            or not cls._optional_non_empty_string(state.xml_file)
            or not cls._optional_non_empty_string(state.manifest_id)
            or not cls._optional_non_empty_string(state.video_id)
        ):
            return False

        boolean_fields = (
            'video_upload_rejected',
            'caption_uploaded',
            'caption_refresh_required',
            'playlist_inserted',
            'youtube_processed',
            'description_updated',
            'ambiguous',
        )
        if any(
            type(getattr(state, name)) is not bool
            for name in boolean_fields
        ):
            return False

        optional_string_fields = (
            'title',
            'stream_title',
            'start_time',
            'caption_status',
            'reason',
            'caption_track_id',
            'description_fingerprint',
            'upload_started_at',
            'retry_at',
            'stage',
            'status',
            'error_stage',
        )
        if any(
            not cls._optional_non_empty_string(getattr(state, name))
            for name in optional_string_fields
        ):
            return False
        if state.error_message is not None and not isinstance(
            state.error_message, str
        ):
            return False

        if (
            not cls._optional_non_negative_number(state.duration)
            or not cls._non_negative_integer(state.attempt)
            or not cls._optional_non_negative_integer(
                state.caption_source_xml_size
            )
            or not cls._optional_non_negative_integer(
                state.caption_source_xml_mtime_ns
            )
            or not cls._optional_non_negative_integer(state.source_size)
            or not cls._optional_non_negative_integer(state.source_mtime_ns)
        ):
            return False
        if (
            not isinstance(state.deleted_paths, tuple)
            or any(
                not cls._non_empty_string(path)
                for path in state.deleted_paths
            )
        ):
            return False

        timestamp_fields = ('start_time', 'upload_started_at', 'retry_at')
        if any(
            value is not None and not cls._aware_instant(value)
            for value in (getattr(state, name) for name in timestamp_fields)
        ):
            return False
        return True

    @staticmethod
    def _non_empty_string(value):
        return isinstance(value, str) and bool(value)

    @classmethod
    def _optional_non_empty_string(cls, value):
        return value is None or cls._non_empty_string(value)

    @staticmethod
    def _non_negative_integer(value):
        return type(value) is int and value >= 0

    @classmethod
    def _optional_non_negative_integer(cls, value):
        return value is None or cls._non_negative_integer(value)

    @staticmethod
    def _optional_non_negative_number(value):
        return (
            value is None
            or (
                not isinstance(value, bool)
                and isinstance(value, (int, float))
                and math.isfinite(value)
                and value >= 0
            )
        )

    @staticmethod
    def _aware_instant(value):
        normalized = (
            value[:-1] + '+00:00'
            if value.endswith(('Z', 'z'))
            else value
        )
        try:
            instant = datetime.fromisoformat(normalized)
            return instant.tzinfo is not None and instant.utcoffset() is not None
        except (TypeError, ValueError):
            return False

    @staticmethod
    def _inconsistent_lifecycle(state):
        if (
            state.ambiguous is True
            or state.event not in _KNOWN_FILE_EVENTS
            or state.event == 'ambiguous'
        ):
            return True
        remote_evidence = any((
            state.youtube_processed is True,
            state.caption_uploaded is True,
            state.playlist_inserted is True,
            state.description_updated is True,
        ))
        if remote_evidence and not state.video_id:
            return True
        if (
            state.event == 'youtube_processed'
            and state.youtube_processed is not True
        ):
            return True
        if (
            state.event == 'caption_uploaded'
            and state.caption_uploaded is not True
        ):
            return True
        if (
            state.event == 'playlist_inserted'
            and state.playlist_inserted is not True
        ):
            return True
        if state.event == 'description_updated' and (
            state.description_updated is not True
            or not state.description_fingerprint
        ):
            return True
        if state.event == 'caption_status' and not state.caption_status:
            return True
        if state.event == 'caption_source_frozen' and (
            not state.xml_file
            or state.caption_source_xml_size is None
            or state.caption_source_xml_mtime_ns is None
        ):
            return True
        if state.event == 'stage_retry_scheduled' and (
            not state.stage
            or not state.status
            or not state.retry_at
            or not StateAwareCleanup._aware_instant(state.retry_at)
        ):
            return True
        if state.event == 'fatal' and not state.error_stage:
            return True
        if state.event == 'upload_started' and (
            not state.title
            or state.duration is None
            or not state.upload_started_at
            or not StateAwareCleanup._aware_instant(state.upload_started_at)
        ):
            return True
        if state.event == 'video_upload_rejected' and (
            state.video_upload_rejected is not True
        ):
            return True
        if state.event == 'video_uploaded' and not state.video_id:
            return True
        if (
            state.event == 'caption_status'
            and (
                state.caption_uploaded
                != (state.caption_status in _TERMINAL_CAPTION_STATUSES)
            )
        ):
            return True
        return False

    def _control_protected_paths(self, replay, manifest_index):
        protected = set()
        if replay.session.state in _ACTIVE_SESSION_STATES:
            protected.update(self._paired_paths(replay.session.session_paths))

        for request in replay.pending_resettles:
            source = manifest_index.get(request.source_manifest_id)
            if source is not None:
                protected.update(self._manifest_paths(source))

        for manifest in replay.manifests:
            if not manifest.invalidated:
                continue
            chain, safely_completed = self._replacement_chain(
                manifest, manifest_index
            )
            if not safely_completed:
                for member in chain:
                    protected.update(self._manifest_paths(member))
        return protected

    @classmethod
    def _control_graph_valid(cls, replay):
        try:
            return cls._validate_control_graph(replay)
        except (AttributeError, TypeError, ValueError):
            return False

    @classmethod
    def _validate_control_graph(cls, replay):
        if not isinstance(replay.files, Mapping):
            return False
        if any(
            type(state) is not JournalFileState
            or key != state.fingerprint
            for key, state in replay.files.items()
        ):
            return False

        session = replay.session
        if not cls._session_shape_valid(session, replay.initialized):
            return False

        manifests = tuple(replay.manifests)
        if any(type(item) is not JournalManifest for item in manifests):
            return False
        manifest_index = {}
        for manifest in manifests:
            if (
                manifest.manifest_id in manifest_index
                or not cls._manifest_control_shape_valid(manifest)
            ):
                return False
            manifest_index[manifest.manifest_id] = manifest
        if session.room_id is not None and any(
            item.room_id != session.room_id for item in manifests
        ):
            return False

        pending = tuple(replay.pending_resettles)
        if any(type(item) is not JournalResettleRequest for item in pending):
            return False
        pending_by_source = {}
        for request in pending:
            if request.source_manifest_id in pending_by_source:
                return False
            source = manifest_index.get(request.source_manifest_id)
            if (
                source is None
                or not source.invalidated
                or source.replacement_manifest_id is not None
                or not cls._resettle_shape_valid(request, source)
            ):
                return False
            pending_by_source[request.source_manifest_id] = request

        incoming = set()
        for manifest in manifests:
            if not manifest.invalidated:
                continue
            replacement_id = manifest.replacement_manifest_id
            if replacement_id is None:
                if manifest.manifest_id not in pending_by_source:
                    return False
                continue
            if replacement_id == manifest.manifest_id or replacement_id in incoming:
                return False
            incoming.add(replacement_id)
            replacement = manifest_index.get(replacement_id)
            if replacement is None:
                if not cls._active_replacement_claim(
                    session, manifest, replacement_id
                ):
                    return False
                continue
            if not cls._replacement_continuity_valid(manifest, replacement):
                return False

        for manifest in manifests:
            seen = set()
            current = manifest
            while current.replacement_manifest_id is not None:
                if current.manifest_id in seen:
                    return False
                seen.add(current.manifest_id)
                current = manifest_index.get(current.replacement_manifest_id)
                if current is None:
                    break

        for state in replay.files.values():
            if state.manifest_id is not None:
                manifest = manifest_index.get(state.manifest_id)
                if manifest is None or state.file not in manifest.flv_paths:
                    return False

        return cls._pending_deletions_valid(replay)

    @classmethod
    def _session_shape_valid(cls, session, initialized):
        if type(session) is not JournalSessionState:
            return False
        if type(initialized) is not bool:
            return False
        if not isinstance(session.state, SessionState):
            return False
        if session.room_id is not None and not cls._non_negative_integer(
            session.room_id
        ):
            return False
        if not cls._optional_non_empty_string(session.session_id):
            return False
        if not cls._path_sequence_valid(session.session_paths):
            return False
        if not cls._snapshot_shape_valid(session.snapshot):
            return False
        if not all(
            value is None
            or (
                cls._non_empty_string(value)
                and cls._aware_instant(value)
            )
            for value in (session.quiet_since, session.started_at)
        ):
            return False
        active = session.state in {
            SessionState.SKIP_CURRENT_SESSION,
            SessionState.RECORDING,
            SessionState.SETTLING,
            SessionState.READY,
        }
        if active:
            started = cls._instant(session.started_at)
            quiet = cls._instant(session.quiet_since)
            if (
                not cls._non_empty_string(session.session_id)
                or started is None
                or quiet is None
                or quiet < started
            ):
                return False
            return (
                not initialized
                if session.state is SessionState.SKIP_CURRENT_SESSION
                else initialized
            )
        if session.state not in {
            SessionState.WAITING, SessionState.BASELINING
        }:
            return False
        if any((
            session.session_id is not None,
            bool(session.session_paths),
            session.quiet_since is not None,
            session.started_at is not None,
        )):
            return False
        return (
            initialized
            if session.state is SessionState.WAITING
            else not initialized
        )

    @classmethod
    def _manifest_control_shape_valid(cls, manifest):
        if (
            not cls._non_empty_string(manifest.manifest_id)
            or not cls._non_negative_integer(manifest.room_id)
            or type(manifest.completed) is not bool
            or type(manifest.invalidated) is not bool
            or not cls._path_sequence_valid(
                manifest.flv_paths, suffix='.flv', nonempty=True
            )
            or not cls._snapshot_shape_valid(manifest.snapshot)
        ):
            return False
        started = cls._instant(manifest.started_at)
        settled = cls._instant(manifest.settled_at)
        if started is None or settled is None or settled < started:
            return False
        allowed = set(manifest.flv_paths)
        allowed.update(Path(path).with_suffix('.xml').as_posix()
                       for path in manifest.flv_paths)
        if (
            not set(manifest.flv_paths).issubset(manifest.snapshot)
            or not set(manifest.snapshot).issubset(allowed)
        ):
            return False
        if manifest.invalidated:
            invalidated = cls._instant(manifest.invalidated_at)
            return bool(
                not manifest.completed
                and invalidated is not None
                and invalidated >= settled
                and cls._non_empty_string(manifest.invalidation_reason)
                and cls._path_sequence_valid(
                    manifest.changed_paths, nonempty=True
                )
                and set(manifest.changed_paths).issubset(allowed)
                and cls._optional_non_empty_string(
                    manifest.replacement_manifest_id
                )
            )
        return bool(
            manifest.invalidated_at is None
            and manifest.invalidation_reason is None
            and not manifest.changed_paths
            and manifest.replacement_manifest_id is None
        )

    @classmethod
    def _resettle_shape_valid(cls, request, source):
        return bool(
            cls._non_empty_string(request.reason)
            and cls._path_sequence_valid(request.changed_paths, nonempty=True)
            and request.reason == source.invalidation_reason
            and request.changed_paths == source.changed_paths
            and cls._instant(request.settled_at)
            == cls._instant(source.settled_at)
            and cls._instant(request.detected_at)
            == cls._instant(source.invalidated_at)
        )

    @classmethod
    def _active_replacement_claim(cls, session, source, replacement_id):
        return bool(
            session.state in {
                SessionState.RECORDING, SessionState.SETTLING
            }
            and session.session_id == replacement_id
            and session.room_id == source.room_id
            and cls._instant(session.started_at)
            == cls._instant(source.started_at)
        )

    @classmethod
    def _replacement_continuity_valid(cls, source, replacement):
        invalidated = cls._instant(source.invalidated_at)
        replacement_settled = cls._instant(replacement.settled_at)
        if (
            source.room_id != replacement.room_id
            or cls._instant(source.started_at)
            != cls._instant(replacement.started_at)
            or invalidated is None
            or replacement_settled is None
            or replacement_settled < invalidated
        ):
            return False
        for path in source.flv_paths:
            if (
                path not in replacement.flv_paths
                or source.snapshot.get(path) != replacement.snapshot.get(path)
            ):
                return False
        return True

    @classmethod
    def _pending_deletions_valid(cls, replay):
        sources = set()
        quarantines = set()
        for intent in replay.pending_deletions:
            if type(intent) is not JournalDeleteIntent:
                return False
            source_key = (intent.fingerprint, intent.original_path)
            if (
                source_key in sources
                or intent.quarantine_path in quarantines
                or type(intent.source_deleted) is not bool
                or any(
                    not cls._non_negative_integer(value)
                    for value in (
                        intent.dev, intent.ino, intent.size, intent.mtime_ns
                    )
                )
                or not cls._non_empty_string(intent.reason)
                or not cls._normalized_absolute(intent.original_path)
                or not cls._safe_quarantine_path(intent.quarantine_path)
            ):
                return False
            state = replay.files.get(intent.fingerprint)
            owners = {
                item.fingerprint for item in replay.files.values()
                if intent.original_path in cls._state_control_owned_paths(item)
            }
            if (
                state is None
                or owners != {intent.fingerprint}
                or intent.source_deleted
                != (intent.original_path in state.deleted_paths)
            ):
                return False
            sources.add(source_key)
            quarantines.add(intent.quarantine_path)
        return True

    @classmethod
    def _state_control_owned_paths(cls, state):
        owned = set()
        if cls._non_empty_string(state.file):
            owned.add(state.file)
            if (
                Path(state.file).suffix.lower() == '.flv'
                and state.event != 'baseline'
            ):
                owned.add(str(Path(state.file).with_suffix('.xml')))
        if cls._non_empty_string(state.xml_file):
            owned.add(state.xml_file)
        return owned

    @classmethod
    def _path_sequence_valid(cls, paths, *, suffix=None, nonempty=False):
        if not isinstance(paths, (tuple, list)) or (nonempty and not paths):
            return False
        normalized = []
        for value in paths:
            if not cls._normalized_absolute(value):
                return False
            if suffix is not None and Path(value).suffix.lower() != suffix:
                return False
            normalized.append(value)
        return len(normalized) == len(set(normalized))

    @classmethod
    def _snapshot_shape_valid(cls, snapshot):
        if not isinstance(snapshot, Mapping):
            return False
        normalized = set()
        for path, identity in snapshot.items():
            if (
                not cls._normalized_absolute(path)
                or cls._lexical_absolute(path) in normalized
                or not isinstance(identity, (tuple, list))
                or len(identity) != 2
                or any(not cls._non_negative_integer(value) for value in identity)
            ):
                return False
            normalized.add(cls._lexical_absolute(path))
        return True

    @staticmethod
    def _normalized_absolute(value):
        return bool(
            isinstance(value, str)
            and value
            and '\0' not in value
            and os.path.isabs(value)
            and not value.startswith('//')
            and os.path.normpath(value) == value
        )

    @staticmethod
    def _safe_quarantine_path(value):
        parts = Path(value).parts if isinstance(value, str) else ()
        return bool(
            isinstance(value, str)
            and not os.path.isabs(value)
            and os.path.normpath(value) == value
            and len(parts) == 2
            and parts[0] == QUARANTINE_DIRECTORY
            and parts[1] not in ('', '.', '..')
        )

    @staticmethod
    def _instant(value):
        if not isinstance(value, str) or not value:
            return None
        normalized = value[:-1] + '+00:00' if value.endswith(('Z', 'z')) else value
        try:
            instant = datetime.fromisoformat(normalized)
            if instant.tzinfo is None or instant.utcoffset() is None:
                return None
            return instant
        except (TypeError, ValueError):
            return None

    @classmethod
    def _all_replay_paths(cls, replay):
        paths = set()

        def add(value):
            if cls._non_empty_string(value):
                paths.add(cls._lexical_absolute(value))

        for state in replay.files.values():
            add(getattr(state, 'file', None))
            add(getattr(state, 'xml_file', None))
        for manifest in replay.manifests:
            for value in getattr(manifest, 'flv_paths', ()):
                add(value)
            snapshot = getattr(manifest, 'snapshot', {})
            if isinstance(snapshot, Mapping):
                for value in snapshot:
                    add(value)
            for value in getattr(manifest, 'changed_paths', ()):
                add(value)
        session = replay.session
        for value in getattr(session, 'session_paths', ()):
            add(value)
        snapshot = getattr(session, 'snapshot', {})
        if isinstance(snapshot, Mapping):
            for value in snapshot:
                add(value)
        for request in replay.pending_resettles:
            for value in getattr(request, 'changed_paths', ()):
                add(value)
        for intent in replay.pending_deletions:
            add(getattr(intent, 'original_path', None))
        return cls._paired_paths(paths)

    @staticmethod
    def _replacement_chain(manifest, manifest_index):
        chain = []
        seen = set()
        current = manifest
        while current is not None and current.manifest_id not in seen:
            chain.append(current)
            seen.add(current.manifest_id)
            if not current.invalidated:
                return chain, current.completed
            replacement_id = current.replacement_manifest_id
            if replacement_id is None:
                return chain, False
            current = manifest_index.get(replacement_id)
        return chain, False

    @classmethod
    def _manifest_paths(cls, manifest):
        paths = set(manifest.snapshot)
        paths.update(manifest.flv_paths)
        return cls._paired_paths(paths)

    @staticmethod
    def _paired_paths(paths):
        paired = set()
        for raw_path in paths:
            path = Path(raw_path)
            paired.add(path)
            suffix = path.suffix.lower()
            if suffix == '.flv':
                paired.add(path.with_suffix('.xml'))
            elif suffix == '.xml':
                paired.add(path.with_suffix('.flv'))
        return paired

    def _safe_regular_file(self, path):
        try:
            file_stat = path.lstat()
            parent = path.parent.resolve(strict=True)
        except OSError:
            return False, None
        if stat.S_ISLNK(file_stat.st_mode) or not stat.S_ISREG(file_stat.st_mode):
            return False, None
        if file_stat.st_nlink != 1:
            return False, None
        try:
            parent.relative_to(self.root)
        except ValueError:
            return False, None
        return True, file_stat

    @staticmethod
    def _matches_required_identity(
        path,
        file_stat,
        manifest,
        state,
        *,
        is_xml,
    ):
        if file_stat is None:
            return False
        expected = (
            manifest.snapshot.get(str(path))
            if manifest is not None else None
        )
        current = (file_stat.st_size, file_stat.st_mtime_ns)
        if state.event == 'baseline':
            return state.fingerprint == baseline_fingerprint(
                path, file_stat.st_size, file_stat.st_mtime_ns
            )
        if expected is not None:
            return current == tuple(expected)
        if not is_xml:
            return current == (state.source_size, state.source_mtime_ns)
        size = state.caption_source_xml_size
        mtime_ns = state.caption_source_xml_mtime_ns
        if (
            not StateAwareCleanup._non_empty_string(state.xml_file)
            or StateAwareCleanup._lexical_absolute(state.xml_file) != path
            or isinstance(size, bool)
            or not isinstance(size, int)
            or size < 0
            or isinstance(mtime_ns, bool)
            or not isinstance(mtime_ns, int)
            or mtime_ns < 0
        ):
            return False
        return current == (size, mtime_ns)

    @staticmethod
    def _stat_identity(file_stat):
        return (
            file_stat.st_dev,
            file_stat.st_ino,
            file_stat.st_size,
            file_stat.st_mtime_ns,
        )

    @staticmethod
    def _lstat(path):
        try:
            return path.lstat()
        except OSError:
            return None

    @staticmethod
    def _ordered(paths):
        return tuple(sorted(paths, key=str))

    @staticmethod
    def _log_exhausted(usage):
        logging.getLogger(__name__).critical(
            'Disk usage remains at %s%%; no eligible Bililive source paths '
            'remain',
            usage,
        )

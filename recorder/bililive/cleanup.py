import logging
import math
import os
import shutil
import stat
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from recorder.bililive.models import SessionState


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
        usage = self.disk_usage(self.root)
        if usage < DISK_CLEANUP_THRESHOLD_PERCENT:
            return CleanupResult((), (), usage, False)

        replay = self.journal.replay()
        manifest_groups = {}
        for item in replay.manifests:
            if self._non_empty_string(item.manifest_id):
                manifest_groups.setdefault(item.manifest_id, []).append(item)
        manifest_index = {
            manifest_id: items[0]
            for manifest_id, items in manifest_groups.items()
            if len(items) == 1
        }
        protected_by_control = self._control_protected_paths(
            replay, manifest_index
        )
        assessments = {}
        fingerprints = {}
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
            for path, eligible, is_xml, identity_optional in self._state_paths(
                state, relationship_valid
            ):
                if relationship_valid and str(path) in state.deleted_paths:
                    continue
                fingerprints.setdefault(path, state.fingerprint)
                safe, file_stat = self._safe_regular_file(path)
                frozen = self._matches_required_identity(
                    path,
                    file_stat,
                    manifest,
                    state,
                    is_xml=is_xml,
                    identity_optional=identity_optional,
                )
                allowed = bool(eligible and safe and frozen)
                assessments.setdefault(path, []).append(allowed)
                if safe and file_stat is not None:
                    identities[path] = self._stat_identity(file_stat)

        protected = set(protected_by_control)
        candidates = []
        for path, path_assessments in assessments.items():
            if path in protected_by_control or not all(path_assessments):
                protected.add(path)
                continue
            file_stat = self._lstat(path)
            if file_stat is None:
                protected.add(path)
                continue
            candidates.append(_Candidate(
                path=path,
                fingerprint=fingerprints[path],
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

        deleted = []
        for candidate in candidates:
            if usage < DISK_CLEANUP_THRESHOLD_PERCENT:
                break
            safe, current_stat = self._safe_regular_file(candidate.path)
            if (
                not safe
                or current_stat is None
                or self._stat_identity(current_stat) != candidate.identity
            ):
                protected.add(candidate.path)
                continue
            candidate.path.unlink()
            deleted.append(candidate.path)
            self.journal.append(
                'source_deleted',
                fingerprint=candidate.fingerprint,
                path=str(candidate.path),
                reason=_DELETE_REASON,
            )
            usage = self.disk_usage(self.root)

        exhausted = usage >= DISK_CLEANUP_THRESHOLD_PERCENT
        if exhausted:
            self._log_exhausted(usage)
        return CleanupResult(
            tuple(deleted), self._ordered(protected), usage, exhausted
        )

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
                yield path, False, path.suffix.lower() == '.xml', False
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
        yield (
            video_path, video_eligible, False,
            baseline_or_ignored,
        )
        if claimed_xml_path is None and not os.path.lexists(xml_path):
            return
        yield xml_path, xml_eligible, True, baseline_or_ignored

    @classmethod
    def _state_binding_valid(cls, state):
        video_path = cls._lexical_absolute(state.file)
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
        identity_optional,
    ):
        if file_stat is None:
            return False
        expected = (
            manifest.snapshot.get(str(path))
            if manifest is not None else None
        )
        current = (file_stat.st_size, file_stat.st_mtime_ns)
        if expected is not None:
            return current == tuple(expected)
        if identity_optional:
            return True
        if not is_xml:
            return manifest is None
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

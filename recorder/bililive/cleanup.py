import logging
import os
import shutil
import stat
from dataclasses import dataclass
from pathlib import Path

from recorder.bililive.models import SessionState


DISK_CLEANUP_THRESHOLD_PERCENT = 85


_IGNORED_EVENTS = frozenset({
    'ignored_invalid',
    'ignored_tiny',
    'ignored_invalid_tail',
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
        manifest_index = {
            item.manifest_id: item for item in replay.manifests
        }
        protected_by_control = self._control_protected_paths(
            replay, manifest_index
        )
        assessments = {}
        fingerprints = {}
        identities = {}

        for state in states:
            manifest = manifest_index.get(state.manifest_id)
            if manifest is not None and manifest.invalidated:
                # An invalidated generation is either protected by its resettle
                # chain or superseded by a safely completed replacement.
                continue
            for path, eligible in self._state_paths(state):
                if str(path) in state.deleted_paths:
                    continue
                fingerprints.setdefault(path, state.fingerprint)
                safe, file_stat = self._safe_regular_file(path)
                frozen = self._matches_frozen_identity(
                    path, file_stat, manifest
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

    def _state_paths(self, state):
        baseline_or_ignored = (
            state.event == 'baseline' or state.event in _IGNORED_EVENTS
        )
        if state.file is not None:
            yield Path(state.file), (
                baseline_or_ignored or state.youtube_processed
            )
        if state.xml_file is not None:
            xml_path = Path(state.xml_file)
        elif state.file is not None:
            xml_path = Path(state.file).with_suffix('.xml')
            if not os.path.lexists(xml_path):
                return
        else:
            return
        yield xml_path, baseline_or_ignored or state.caption_uploaded

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
    def _matches_frozen_identity(path, file_stat, manifest):
        if file_stat is None or manifest is None:
            return True
        expected = manifest.snapshot.get(str(path))
        if expected is None:
            return True
        return (file_stat.st_size, file_stat.st_mtime_ns) == tuple(expected)

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

import errno
import fcntl
import hashlib
import json
import math
import os
import threading
from dataclasses import fields, replace
from datetime import datetime, timezone
from pathlib import Path

from recorder.bililive.models import (
    JournalFileState,
    JournalManifest,
    JournalReplay,
    JournalSessionState,
    SessionState,
)


class JournalCorruptError(ValueError):
    pass


class AlreadyRunningError(RuntimeError):
    pass


_FILE_FIELD_NAMES = frozenset(field.name for field in fields(JournalFileState))
_INITIAL_FILE_EVENTS = frozenset({
    'baseline',
    'file_ready',
    'ignored_invalid',
    'ignored_tiny',
    'ignored_invalid_tail',
})
_FILE_EVENT_UPDATES = {
    'baseline': frozenset({'manifest_id', 'file', 'xml_file'}),
    'file_ready': frozenset({
        'manifest_id', 'file', 'xml_file', 'title', 'start_time', 'duration',
        'caption_status',
    }),
    'ignored_invalid': frozenset({
        'manifest_id', 'file', 'xml_file', 'title', 'start_time', 'duration',
        'caption_status', 'error_stage', 'error_message',
    }),
    'ignored_tiny': frozenset({
        'manifest_id', 'file', 'xml_file', 'title', 'start_time', 'duration',
        'caption_status', 'error_stage', 'error_message',
    }),
    'ignored_invalid_tail': frozenset({
        'manifest_id', 'file', 'xml_file', 'title', 'start_time', 'duration',
        'caption_status', 'error_stage', 'error_message',
    }),
    'upload_started': frozenset({
        'file', 'xml_file', 'title', 'duration', 'description_fingerprint',
        'upload_started_at',
    }),
    'video_upload_rejected': frozenset({'error_stage', 'error_message'}),
    'video_uploaded': frozenset({'video_id'}),
    'description_updated': frozenset({'description_fingerprint'}),
    'caption_status': frozenset({'caption_status', 'error_message'}),
    'caption_uploaded': frozenset({'caption_status'}),
    'playlist_inserted': frozenset(),
    'youtube_processed': frozenset(),
    'stage_retry_scheduled': frozenset({
        'retry_at', 'attempt', 'error_stage', 'error_message',
    }),
    'ambiguous': frozenset({'error_stage', 'error_message'}),
    'fatal': frozenset({'error_stage', 'error_message'}),
    'source_deleted': frozenset(),
}


def _require_non_empty_string(record, name, event):
    value = record.get(name)
    if not isinstance(value, str) or not value:
        raise TypeError(f'{event} requires a non-empty {name}')


def _validate_file_record(record, event, existing, enforce_history=True):
    fingerprint = record.get('fingerprint')
    if not isinstance(fingerprint, str) or not fingerprint:
        raise TypeError('fingerprint must be a non-empty string')

    if event in _INITIAL_FILE_EVENTS:
        _require_non_empty_string(record, 'file', event)
    elif existing is None and enforce_history:
        raise ValueError(f'{event} requires an existing file state')
    if (
        enforce_history
        and event in {
            'description_updated',
            'caption_uploaded',
            'playlist_inserted',
            'youtube_processed',
        }
        and existing.video_id is None
    ):
        raise ValueError(f'{event} requires an existing video_id')

    string_fields = {
        'manifest_id', 'file', 'xml_file', 'title', 'start_time', 'video_id',
        'caption_status', 'description_fingerprint', 'upload_started_at',
        'retry_at', 'error_stage',
    }
    for name in string_fields.intersection(_FILE_EVENT_UPDATES[event], record):
        value = record[name]
        if value is not None and (not isinstance(value, str) or not value):
            raise TypeError(f'{event} requires {name} to be null or a string')
    if 'error_message' in _FILE_EVENT_UPDATES[event] and 'error_message' in record:
        if record['error_message'] is not None and not isinstance(
            record['error_message'], str
        ):
            raise TypeError(
                f'{event} requires error_message to be null or a string'
            )

    if 'duration' in _FILE_EVENT_UPDATES[event] and 'duration' in record:
        duration = record['duration']
        if duration is not None and (
            isinstance(duration, bool)
            or not isinstance(duration, (int, float))
            or not math.isfinite(duration)
            or duration < 0
        ):
            raise TypeError(f'{event} requires a finite non-negative duration')

    for alias in ('stage', 'message', 'reason'):
        if (
            alias in record
            and record[alias] is not None
            and not isinstance(record[alias], str)
        ):
            raise TypeError(f'{event} requires {alias} to be null or a string')

    if event == 'upload_started':
        _require_non_empty_string(record, 'title', event)
        _require_non_empty_string(record, 'upload_started_at', event)
        duration = record.get('duration')
        if (
            isinstance(duration, bool)
            or not isinstance(duration, (int, float))
            or not math.isfinite(duration)
            or duration < 0
        ):
            raise TypeError('upload_started requires a finite non-negative duration')
        if existing is not None and existing.video_id is not None:
            raise ValueError('upload_started cannot replace an existing video_id')
    elif event == 'video_uploaded':
        _require_non_empty_string(record, 'video_id', event)
    elif event == 'description_updated':
        _require_non_empty_string(record, 'description_fingerprint', event)
    elif event == 'caption_status':
        _require_non_empty_string(record, 'caption_status', event)
    elif event == 'stage_retry_scheduled':
        _require_non_empty_string(record, 'retry_at', event)
        attempt = record.get('attempt')
        if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt < 0:
            raise TypeError(
                'stage_retry_scheduled requires a non-negative integer attempt'
            )
    elif event == 'source_deleted':
        _require_non_empty_string(record, 'path', event)
        _require_non_empty_string(record, 'reason', event)


def _file_event_updates(record, event):
    updates = {
        key: record[key]
        for key in _FILE_EVENT_UPDATES[event]
        if key in record and key in _FILE_FIELD_NAMES
    }
    if 'stage' in record and event in {
        'stage_retry_scheduled', 'fatal', 'video_upload_rejected'
    }:
        updates['error_stage'] = record['stage']
    if 'message' in record and event in {
        'ambiguous', 'fatal', 'video_upload_rejected'
    }:
        updates['error_message'] = record['message']
    if 'reason' in record and event in _INITIAL_FILE_EVENTS:
        updates['error_message'] = record['reason']

    if event == 'upload_started':
        updates.update(
            video_id=None,
            video_upload_rejected=False,
            ambiguous=False,
            retry_at=None,
        )
    elif event == 'video_upload_rejected':
        updates.update(
            video_id=None,
            video_upload_rejected=True,
            ambiguous=False,
        )
    elif event == 'video_uploaded':
        updates.update(video_upload_rejected=False, ambiguous=False, retry_at=None)
    elif event == 'ambiguous':
        updates.update(video_upload_rejected=False, ambiguous=True, retry_at=None)
    elif event == 'caption_uploaded':
        updates['caption_uploaded'] = True
    elif event == 'playlist_inserted':
        updates['playlist_inserted'] = True
    elif event == 'youtube_processed':
        updates['youtube_processed'] = True
    return updates


def _validate_optional_string(record, name):
    if name not in record:
        raise TypeError(f'session_state requires {name}')
    value = record[name]
    if value is not None and (not isinstance(value, str) or not value):
        raise TypeError(f'{name} must be null or a non-empty string')


def _reduce_initialized(replay, record):
    del record
    return replace(replay, initialized=True)


def _reduce_session_state(replay, record):
    required = {
        'state', 'session_id', 'session_paths', 'snapshot', 'quiet_since',
        'started_at',
    }
    missing = required.difference(record)
    if missing:
        raise TypeError(
            'session_state missing required fields: ' + ', '.join(sorted(missing))
        )
    try:
        state = SessionState(record['state'])
    except (TypeError, ValueError) as exception:
        raise TypeError('session_state has an invalid state') from exception

    _validate_optional_string(record, 'session_id')
    _validate_optional_string(record, 'quiet_since')
    _validate_optional_string(record, 'started_at')

    session_paths = record['session_paths']
    if not isinstance(session_paths, (list, tuple)) or any(
        not isinstance(path, str) or not path for path in session_paths
    ):
        raise TypeError('session_paths must be a list of non-empty strings')

    raw_snapshot = record['snapshot']
    if not isinstance(raw_snapshot, dict):
        raise TypeError('snapshot must be an object')
    snapshot = {}
    for path, identity in raw_snapshot.items():
        if not isinstance(path, str) or not path:
            raise TypeError('snapshot paths must be non-empty strings')
        if not isinstance(identity, (list, tuple)) or len(identity) != 2:
            raise TypeError('snapshot identities must be [size, mtime_ns] lists')
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in identity
        ):
            raise TypeError('snapshot size and mtime_ns must be non-negative integers')
        snapshot[path] = tuple(identity)

    session = JournalSessionState(
        state=state,
        session_id=record['session_id'],
        session_paths=tuple(session_paths),
        snapshot=snapshot,
        quiet_since=record['quiet_since'],
        started_at=record['started_at'],
    )
    return replace(replay, session=session)


def _validate_manifest_id(record, event):
    _require_non_empty_string(record, 'manifest_id', event)


def _reduce_manifest_ready(replay, record):
    event = 'session_manifest_ready'
    _validate_manifest_id(record, event)
    for name in ('started_at', 'settled_at'):
        _require_non_empty_string(record, name, event)
    room_id = record.get('room_id')
    if isinstance(room_id, bool) or not isinstance(room_id, int):
        raise TypeError(f'{event} requires an integer room_id')
    flv_paths = record.get('flv_paths')
    if not isinstance(flv_paths, (list, tuple)) or any(
        not isinstance(path, str) or not path for path in flv_paths
    ):
        raise TypeError(f'{event} requires a list of non-empty flv_paths')

    manifest = JournalManifest(
        manifest_id=record['manifest_id'],
        room_id=room_id,
        started_at=record['started_at'],
        settled_at=record['settled_at'],
        flv_paths=tuple(flv_paths),
    )
    manifests = list(replay.manifests)
    for index, existing in enumerate(manifests):
        if existing.manifest_id == manifest.manifest_id:
            if existing.completed:
                existing_identity = replace(existing, completed=False)
                if existing_identity != manifest:
                    raise ValueError(
                        'cannot replace a completed manifest with different data'
                    )
                manifest = replace(manifest, completed=True)
            manifests[index] = manifest
            break
    else:
        manifests.append(manifest)
    manifests.sort(key=lambda item: item.settled_at)
    return replace(replay, manifests=tuple(manifests))


def _reduce_manifest_completed(replay, record):
    event = 'session_manifest_completed'
    _validate_manifest_id(record, event)
    manifests = list(replay.manifests)
    for index, manifest in enumerate(manifests):
        if manifest.manifest_id == record['manifest_id']:
            manifests[index] = replace(manifest, completed=True)
            return replace(replay, manifests=tuple(manifests))
    raise ValueError(
        'session_manifest_completed requires an existing ready manifest'
    )


_CONTROL_REDUCERS = {
    'initialized': _reduce_initialized,
    'session_state': _reduce_session_state,
    'session_manifest_ready': _reduce_manifest_ready,
    'session_manifest_completed': _reduce_manifest_completed,
}


def _validate_append_record(record):
    if not isinstance(record, dict):
        raise TypeError('journal event must be an object')
    event = record.get('event')
    if not isinstance(event, str):
        raise TypeError('event must be a string')
    if event in _FILE_EVENT_UPDATES:
        _validate_file_record(record, event, None, enforce_history=False)
        return
    if event == 'initialized':
        return
    if event == 'session_state':
        _reduce_session_state(_empty_replay(), record)
        return
    if event == 'session_manifest_ready':
        _reduce_manifest_ready(_empty_replay(), record)
        return
    if event == 'session_manifest_completed':
        _validate_manifest_id(record, event)
        return
    raise ValueError(f'unknown event {event!r}')


def baseline_fingerprint(path, size, mtime_ns):
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise ValueError('size must be a non-negative integer')
    if isinstance(mtime_ns, bool) or not isinstance(mtime_ns, int) or mtime_ns < 0:
        raise ValueError('mtime_ns must be a non-negative integer')
    identity = f'{Path(path).resolve()}\0{size}\0{mtime_ns}'.encode('utf8')
    return 'baseline:' + hashlib.sha256(identity).hexdigest()


def _fsync_directory(path):
    flags = os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0)
    file_descriptor = os.open(str(path), flags)
    try:
        os.fsync(file_descriptor)
    finally:
        os.close(file_descriptor)


def _ensure_directory(path):
    missing = []
    candidate = path
    while not candidate.exists() and candidate.parent != candidate:
        missing.append(candidate)
        candidate = candidate.parent
    path.mkdir(parents=True, exist_ok=True)
    for created in reversed(missing):
        _fsync_directory(created.parent)


class ProcessLock:
    def __init__(self, state_dir):
        self.state_dir = Path(state_dir)
        _ensure_directory(self.state_dir)
        self.path = self.state_dir / 'monitor.lock'
        lock_file_existed = self.path.exists()
        self._file = self.path.open('a+b')
        if not lock_file_existed:
            self._file.flush()
            os.fsync(self._file.fileno())
            _fsync_directory(self.state_dir)
        try:
            fcntl.flock(self._file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exception:
            self._file.close()
            self._file = None
            if exception.errno in (errno.EACCES, errno.EAGAIN):
                raise AlreadyRunningError(
                    f'Bililive monitor is already running: {self.path}'
                ) from exception
            raise

    def close(self):
        lock_file = self._file
        if lock_file is None:
            return
        self._file = None
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        finally:
            lock_file.close()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception, traceback):
        self.close()


def _empty_replay():
    return JournalReplay(
        files={},
        manifests=(),
        session=JournalSessionState(
            state=SessionState.BASELINING,
            session_id=None,
            session_paths=(),
            snapshot={},
            quiet_since=None,
            started_at=None,
        ),
        initialized=False,
    )


class JsonlJournal:
    def __init__(self, path):
        self.path = Path(path)
        self._mutex = threading.Lock()

    def append(self, event, **fields):
        record = dict(fields, event=event)
        with self._mutex:
            _validate_append_record(record)
            journal_existed = self.path.exists()
            existing_payload = self.path.read_bytes() if journal_existed else b''
            replay, torn_offset, needs_separator = self._replay_payload(
                existing_payload
            )
            self._reduce(replay, record)
            record['recorded_at'] = datetime.now(timezone.utc).isoformat()
            payload = json.dumps(
                record,
                ensure_ascii=False,
                separators=(',', ':'),
                allow_nan=False,
            ).encode('utf8') + b'\n'
            _ensure_directory(self.path.parent)
            mode = 'r+b' if journal_existed else 'w+b'
            with self.path.open(mode) as journal_file:
                if torn_offset is not None:
                    journal_file.truncate(torn_offset)
                journal_file.seek(0, os.SEEK_END)
                if needs_separator:
                    journal_file.write(b'\n')
                journal_file.write(payload)
                journal_file.flush()
                os.fsync(journal_file.fileno())
            if not journal_existed:
                _fsync_directory(self.path.parent)

    def replay(self):
        with self._mutex:
            if not self.path.exists():
                return _empty_replay()
            payload = self.path.read_bytes()
            replay, _, _ = self._replay_payload(payload)
            return replay

    @classmethod
    def _replay_payload(cls, payload):
        replay = _empty_replay()
        if not payload:
            return replay, None, False

        lines = payload.split(b'\n')
        final_is_complete = payload.endswith(b'\n')
        if final_is_complete:
            lines.pop()

        byte_offset = 0
        for line_number, line in enumerate(lines, 1):
            is_unterminated_final = (
                not final_is_complete and line_number == len(lines)
            )
            try:
                record = json.loads(line.decode('utf8'))
            except (UnicodeDecodeError, json.JSONDecodeError) as exception:
                if is_unterminated_final:
                    return replay, byte_offset, False
                raise JournalCorruptError(
                    'Invalid journal JSON on line '
                    f'{line_number} at byte offset {byte_offset}: {exception}'
                ) from exception

            try:
                replay = cls._reduce(replay, record)
            except (TypeError, ValueError, KeyError) as exception:
                raise JournalCorruptError(
                    'Invalid journal event on line '
                    f'{line_number} at byte offset {byte_offset}: {exception}'
                ) from exception
            byte_offset += len(line) + 1
        return replay, None, not final_is_complete

    @staticmethod
    def _reduce(replay, record):
        if not isinstance(record, dict):
            raise TypeError('journal event must be an object')
        event = record['event']
        if not isinstance(event, str):
            raise TypeError('event must be a string')
        control_reducer = _CONTROL_REDUCERS.get(event)
        if control_reducer is not None:
            return control_reducer(replay, record)
        if event not in _FILE_EVENT_UPDATES:
            raise ValueError(f'unknown event {event!r}')

        fingerprint = record.get('fingerprint')
        existing = replay.files.get(fingerprint)
        _validate_file_record(record, event, existing)
        updates = _file_event_updates(record, event)
        if existing is None:
            state = JournalFileState(fingerprint=fingerprint, event=event, **updates)
        else:
            state = replace(existing, event=event, **updates)
        replay.files[fingerprint] = state
        if event == 'baseline':
            return replace(replay, initialized=True)
        return replay

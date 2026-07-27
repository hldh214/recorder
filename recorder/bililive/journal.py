import errno
import fcntl
import hashlib
import json
import math
import os
import threading
from collections.abc import Mapping
from dataclasses import dataclass, fields, replace
from datetime import datetime, timezone
from pathlib import Path

from recorder.bililive.models import (
    JournalDeleteAbort,
    JournalDeleteIntent,
    JournalFileState,
    JournalManifest,
    JournalReplay,
    JournalResettleRequest,
    JournalSessionState,
    SessionState,
)


class JournalCorruptError(ValueError):
    pass


class AlreadyRunningError(RuntimeError):
    pass


_FILE_FIELD_NAMES = frozenset(field.name for field in fields(JournalFileState))
_JOURNAL_LOCKS = {}
_JOURNAL_LOCKS_GUARD = threading.Lock()
_INITIAL_FILE_EVENTS = frozenset({
    'baseline',
    'file_ready',
    'ignored_invalid',
    'ignored_tiny',
    'ignored_invalid_tail',
})
_IGNORED_FILE_EVENTS = frozenset({
    'ignored_invalid',
    'ignored_tiny',
    'ignored_invalid_tail',
})
_DELETE_TRANSACTION_EVENTS = frozenset({
    'source_delete_intent',
    'source_deleted',
    'quarantine_removed',
    'source_delete_aborted',
})
_FILE_EVENT_UPDATES = {
    'baseline': frozenset({
        'manifest_id', 'file', 'xml_file', 'source_size', 'source_mtime_ns',
    }),
    'file_ready': frozenset({
        'manifest_id', 'file', 'xml_file', 'title', 'stream_title',
        'start_time', 'duration', 'source_size', 'source_mtime_ns',
        'caption_status',
    }),
    'ignored_invalid': frozenset({
        'manifest_id', 'file', 'xml_file', 'title', 'start_time', 'duration',
        'caption_status', 'reason', 'error_stage', 'error_message',
        'source_size', 'source_mtime_ns',
    }),
    'ignored_tiny': frozenset({
        'manifest_id', 'file', 'xml_file', 'title', 'start_time', 'duration',
        'caption_status', 'reason', 'error_stage', 'error_message',
        'source_size', 'source_mtime_ns',
    }),
    'ignored_invalid_tail': frozenset({
        'manifest_id', 'file', 'xml_file', 'title', 'start_time', 'duration',
        'caption_status', 'reason', 'error_stage', 'error_message',
        'source_size', 'source_mtime_ns',
    }),
    'upload_started': frozenset({
        'file', 'xml_file', 'title', 'duration', 'description_fingerprint',
        'upload_started_at', 'attempt',
    }),
    'video_upload_rejected': frozenset({'error_stage', 'error_message'}),
    'video_uploaded': frozenset({'video_id'}),
    'description_updated': frozenset({'description_fingerprint'}),
    'caption_status': frozenset({'caption_status', 'error_message'}),
    'caption_source_frozen': frozenset({
        'xml_file', 'caption_source_xml_size',
        'caption_source_xml_mtime_ns',
    }),
    'caption_uploaded': frozenset({'caption_status', 'caption_track_id'}),
    'playlist_inserted': frozenset(),
    'youtube_processed': frozenset(),
    'stage_retry_scheduled': frozenset({
        'retry_at', 'attempt', 'stage', 'status', 'error_stage',
        'error_message',
    }),
    'ambiguous': frozenset({'error_stage', 'error_message'}),
    'fatal': frozenset({'error_stage', 'error_message'}),
    'source_deleted': frozenset(),
}


def _require_non_empty_string(record, name, event):
    value = record.get(name)
    if not isinstance(value, str) or not value:
        raise TypeError(f'{event} requires a non-empty {name}')


def _parse_aware_instant(value, name, event):
    if not isinstance(value, str) or not value:
        raise TypeError(f'{event} requires timezone-aware ISO {name}')
    normalized = value[:-1] + '+00:00' if value.endswith(('Z', 'z')) else value
    try:
        instant = datetime.fromisoformat(normalized)
        offset = instant.utcoffset()
    except (TypeError, ValueError) as exception:
        raise ValueError(
            f'{event} requires timezone-aware ISO {name}'
        ) from exception
    if instant.tzinfo is None or offset is None:
        raise ValueError(f'{event} requires timezone-aware ISO {name}')
    return instant.astimezone(timezone.utc)


def _shared_journal_lock(path):
    normalized_path = str(Path(path).resolve())
    with _JOURNAL_LOCKS_GUARD:
        return _JOURNAL_LOCKS.setdefault(normalized_path, threading.RLock())


def canonical_source_path(value):
    if not isinstance(value, str) or not value or '\0' in value:
        raise ValueError('source path must be a non-empty string without NUL')
    normalized = os.path.abspath(os.path.normpath(value))
    if normalized.startswith('//'):
        normalized = '/' + normalized.lstrip('/')
    return normalized


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
    if event in _IGNORED_FILE_EVENTS:
        _require_non_empty_string(record, 'reason', event)

    string_fields = {
        'manifest_id', 'file', 'xml_file', 'title', 'stream_title',
        'start_time', 'video_id', 'caption_status',
        'description_fingerprint', 'upload_started_at', 'retry_at', 'stage',
        'status', 'reason', 'error_stage', 'caption_track_id',
    }
    for name in string_fields.intersection(_FILE_EVENT_UPDATES[event], record):
        value = record[name]
        if value is not None and (not isinstance(value, str) or not value):
            raise TypeError(f'{event} requires {name} to be null or a string')
    for name in ('file', 'xml_file'):
        if name not in _FILE_EVENT_UPDATES[event] or record.get(name) is None:
            continue
        record[name] = canonical_source_path(record[name])
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

    for name in ('source_size', 'source_mtime_ns'):
        if name in _FILE_EVENT_UPDATES[event] and name in record:
            value = record[name]
            if (
                value is not None
                and (
                    isinstance(value, bool)
                    or not isinstance(value, int)
                    or value < 0
                )
            ):
                raise TypeError(
                    f'{event} requires non-negative integer {name}'
                )

    for alias in ('stage', 'message', 'reason'):
        if (
            alias in record
            and record[alias] is not None
            and not isinstance(record[alias], str)
        ):
            raise TypeError(f'{event} requires {alias} to be null or a string')

    if event == 'file_ready' and record.get('start_time') is not None:
        _parse_aware_instant(record['start_time'], 'start_time', event)

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
        if existing is not None and existing.ambiguous:
            raise ValueError('upload_started cannot retry an ambiguous upload')
        _parse_aware_instant(record['upload_started_at'], 'upload_started_at', event)
        attempt = record.get('attempt', 0)
        if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt < 0:
            raise TypeError(
                'upload_started requires a non-negative integer attempt'
            )
    elif event == 'video_upload_rejected':
        if existing is not None and existing.video_id is not None:
            raise ValueError(
                'video_upload_rejected cannot discard an existing video_id'
            )
    elif event == 'video_uploaded':
        _require_non_empty_string(record, 'video_id', event)
        if (
            existing is not None
            and existing.video_id is not None
            and existing.video_id != record['video_id']
        ):
            raise ValueError('video_uploaded cannot replace a different video_id')
    elif event == 'description_updated':
        _require_non_empty_string(record, 'description_fingerprint', event)
    elif event == 'caption_status':
        _require_non_empty_string(record, 'caption_status', event)
    elif event == 'caption_source_frozen':
        _require_non_empty_string(record, 'xml_file', event)
        for name in (
            'caption_source_xml_size', 'caption_source_xml_mtime_ns'
        ):
            value = record.get(name)
            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or value < 0
            ):
                raise TypeError(
                    f'{event} requires non-negative integer {name}'
                )
        if existing is not None:
            requested_identity = (
                canonical_source_path(record['xml_file']),
                record['caption_source_xml_size'],
                record['caption_source_xml_mtime_ns'],
            )
            frozen_identity = (
                existing.xml_file,
                existing.caption_source_xml_size,
                existing.caption_source_xml_mtime_ns,
            )
            if any(value is not None for value in frozen_identity[1:]):
                if requested_identity != frozen_identity:
                    raise ValueError(
                        'caption source identity is immutable within a '
                        'generation'
                    )
            elif existing.xml_file != record['xml_file']:
                raise ValueError(
                    'caption_source_frozen XML path does not match file state'
                )
    elif event == 'stage_retry_scheduled':
        for name in ('stage', 'status', 'retry_at'):
            _require_non_empty_string(record, name, event)
        attempt = record.get('attempt')
        if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt < 0:
            raise TypeError(
                'stage_retry_scheduled requires a non-negative integer attempt'
            )
        _parse_aware_instant(record['retry_at'], 'retry_at', event)
    elif event == 'source_deleted':
        _require_non_empty_string(record, 'path', event)
        _require_non_empty_string(record, 'reason', event)
        if not os.path.isabs(record['path']):
            raise ValueError('source_deleted requires an absolute path')
        record['path'] = canonical_source_path(record['path'])


def _file_event_updates(record, event, existing=None):
    # Extra diagnostics remain in JSONL without entering the stable replay model.
    updates = {
        key: record[key]
        for key in _FILE_EVENT_UPDATES[event]
        if key in record and key in _FILE_FIELD_NAMES
    }
    for name in ('file', 'xml_file'):
        if name in updates and updates[name] is not None:
            updates[name] = canonical_source_path(updates[name])
    if 'stage' in record and event in {
        'stage_retry_scheduled', 'fatal', 'ambiguous', 'video_upload_rejected'
    }:
        updates['error_stage'] = record['stage']
    if 'message' in record and event in {
        'ambiguous', 'fatal', 'video_upload_rejected'
    }:
        updates['error_message'] = record['message']
    if 'reason' in record and event in _INITIAL_FILE_EVENTS:
        updates['error_message'] = record['reason']
    if event == 'file_ready':
        updates['stream_title'] = record.get(
            'stream_title', record.get('title')
        )

    if event == 'upload_started':
        updates.update(
            video_id=None,
            video_upload_rejected=False,
            description_updated=False,
            ambiguous=False,
            retry_at=None,
            attempt=record.get('attempt', 0),
            stage=None,
            status=None,
            error_stage=None,
            error_message=None,
        )
    elif event == 'video_upload_rejected':
        updates.update(
            video_id=None,
            video_upload_rejected=True,
            ambiguous=False,
        )
    elif event == 'video_uploaded':
        updates.update(
            video_upload_rejected=False,
            ambiguous=False,
            retry_at=None,
            stage=None,
            status=None,
            error_stage=None,
            error_message=None,
        )
    elif event == 'description_updated':
        updates['description_updated'] = True
    elif event == 'ambiguous':
        updates.update(
            video_upload_rejected=False,
            ambiguous=True,
            retry_at=None,
            attempt=0,
            stage=None,
            status=None,
        )
    elif event == 'fatal':
        updates.update(retry_at=None, attempt=0, stage=None, status=None)
    elif event == 'caption_uploaded':
        updates.update(
            caption_uploaded=True,
            caption_refresh_required=False,
        )
    elif event == 'playlist_inserted':
        updates['playlist_inserted'] = True
    elif event == 'youtube_processed':
        updates['youtube_processed'] = True
    elif event == 'source_deleted':
        deleted_path = canonical_source_path(record['path'])
        deleted_paths = existing.deleted_paths if existing is not None else ()
        if deleted_path not in deleted_paths:
            deleted_paths += (deleted_path,)
        updates['deleted_paths'] = deleted_paths
    return updates


def _controlled_manifest_migration(replay, existing, state, event):
    if event not in {'file_ready'} | _IGNORED_FILE_EVENTS:
        raise ValueError('manifest migration requires a classification event')
    if _has_publication_lifecycle(existing) and event != 'file_ready':
        raise ValueError(
            'attempted publication migration requires a ready classification'
        )
    manifests = {item.manifest_id: item for item in replay.manifests}
    old = manifests.get(existing.manifest_id)
    target = manifests.get(state.manifest_id)
    if old is None:
        raise ValueError('manifest migration requires the old ready manifest')
    if target is None or target.invalidated or target.completed:
        raise ValueError(
            'manifest migration requires an active ready target manifest'
        )
    xml_path = os.path.splitext(state.file)[0] + '.xml'
    caption_changed = False
    current = old
    visited = set()
    while current.manifest_id != target.manifest_id:
        if current.manifest_id in visited:
            raise ValueError('manifest migration replacement chain contains a cycle')
        visited.add(current.manifest_id)
        if not current.invalidated:
            raise ValueError(
                'manifest migration requires an invalidated replacement chain'
            )
        replacement_id = current.replacement_manifest_id
        replacement = manifests.get(replacement_id)
        if replacement is None:
            raise ValueError(
                'manifest migration replacement chain has a missing link'
            )
        if current.room_id != replacement.room_id:
            raise ValueError('manifest migration cannot cross rooms')
        if _parse_aware_instant(
            current.started_at, 'started_at', 'manifest migration'
        ) != _parse_aware_instant(
            replacement.started_at, 'started_at', 'manifest migration'
        ):
            raise ValueError(
                'manifest migration has a conflicting session chain'
            )
        if _parse_aware_instant(
            replacement.settled_at, 'settled_at', 'manifest migration'
        ) < _parse_aware_instant(
            current.invalidated_at, 'invalidated_at', 'manifest migration'
        ):
            raise ValueError('manifest migration target predates invalidation')
        if (
            state.file not in current.flv_paths
            or state.file not in replacement.flv_paths
        ):
            raise ValueError(
                'manifest migration target does not contain the same file'
            )
        if (
            current.snapshot.get(state.file)
            != replacement.snapshot.get(state.file)
        ):
            raise ValueError(
                'manifest migration has conflicting frozen FLV identity'
            )
        caption_changed = caption_changed or (
            current.snapshot.get(xml_path)
            != replacement.snapshot.get(xml_path)
        )
        current = replacement

    return caption_changed


def _has_publication_lifecycle(state):
    return bool(
        state.event not in _INITIAL_FILE_EVENTS
        or state.upload_started_at
        or state.retry_at
        or state.video_id
        or state.video_upload_rejected
        or state.description_updated
        or state.caption_uploaded
        or state.playlist_inserted
        or state.youtube_processed
        or state.ambiguous
    )


def _migrate_publication_state(existing, classified):
    return replace(
        existing,
        manifest_id=classified.manifest_id,
        file=classified.file,
        xml_file=classified.xml_file,
        stream_title=classified.stream_title,
        start_time=classified.start_time,
        duration=classified.duration,
        source_size=classified.source_size,
        source_mtime_ns=classified.source_mtime_ns,
        caption_source_xml_size=None,
        caption_source_xml_mtime_ns=None,
    )


def _validate_file_binding(replay, state, existing=None, event=None):
    caption_changed = False
    if existing is not None:
        if existing.file is not None and state.file != existing.file:
            raise ValueError(
                f'fingerprint {state.fingerprint!r} cannot change its file path'
            )
        if (
            existing.manifest_id is not None
            and state.manifest_id != existing.manifest_id
        ):
            caption_changed = _controlled_manifest_migration(
                replay, existing, state, event
            )
    owned_paths = _owned_source_paths(state)
    for intent in replay.pending_deletions:
        if (
            not intent.source_deleted
            and intent.fingerprint != state.fingerprint
            and intent.original_path in owned_paths
        ):
            raise ValueError(
                'file state conflicts with a pending deletion owner'
            )
    if state.manifest_id is None or state.file is None:
        return caption_changed
    binding = (state.manifest_id, state.file)
    for other_fingerprint, other in replay.files.items():
        if other_fingerprint == state.fingerprint:
            continue
        if (other.manifest_id, other.file) == binding:
            raise ValueError(
                f'manifest/file binding {binding!r} belongs to both '
                f'{other_fingerprint!r} and {state.fingerprint!r}'
            )
    return caption_changed


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
        'state', 'room_id', 'session_id', 'session_paths', 'snapshot',
        'quiet_since', 'started_at',
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

    room_id = record['room_id']
    if isinstance(room_id, bool) or not isinstance(room_id, int):
        raise TypeError('session_state requires an integer room_id')
    if (
        replay.session.room_id is not None
        and replay.session.room_id != room_id
    ):
        raise ValueError('session_state cannot change the bound room_id')
    if any(manifest.room_id != room_id for manifest in replay.manifests):
        raise ValueError('session_state room_id conflicts with a manifest')

    _validate_optional_string(record, 'session_id')
    _validate_optional_string(record, 'quiet_since')
    _validate_optional_string(record, 'started_at')
    for name in ('quiet_since', 'started_at'):
        if record[name] is not None:
            _parse_aware_instant(record[name], name, 'session_state')

    session_paths = record['session_paths']
    if not isinstance(session_paths, (list, tuple)) or any(
        not isinstance(path, str) or not path for path in session_paths
    ):
        raise TypeError('session_paths must be a list of non-empty strings')

    raw_snapshot = record['snapshot']
    if not isinstance(raw_snapshot, Mapping):
        raise TypeError('snapshot must be an object')
    raw_snapshot = dict(raw_snapshot)
    record['snapshot'] = raw_snapshot
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
        room_id=room_id,
        session_id=record['session_id'],
        session_paths=tuple(session_paths),
        snapshot=snapshot,
        quiet_since=record['quiet_since'],
        started_at=record['started_at'],
    )
    return replace(replay, session=session)


def _validate_manifest_id(record, event):
    _require_non_empty_string(record, 'manifest_id', event)


def _require_normalized_absolute_path(path, event, field):
    normalized = os.path.normpath(path)
    if (
        '\0' in path
        or not os.path.isabs(path)
        or path.startswith('//')
        or normalized != path
    ):
        raise ValueError(
            f'{event} {field} must be a normalized absolute path'
        )
    return normalized


def _reduce_manifest_ready(replay, record):
    event = 'session_manifest_ready'
    _validate_manifest_id(record, event)
    instants = {}
    for name in ('started_at', 'settled_at'):
        _require_non_empty_string(record, name, event)
        instants[name] = _parse_aware_instant(record[name], name, event)
    if instants['settled_at'] < instants['started_at']:
        raise ValueError(f'{event} settled_at cannot be before started_at')
    room_id = record.get('room_id')
    if isinstance(room_id, bool) or not isinstance(room_id, int):
        raise TypeError(f'{event} requires an integer room_id')
    if (
        replay.session.room_id is not None
        and replay.session.room_id != room_id
    ):
        raise ValueError(f'{event} room_id conflicts with the bound session')
    if any(manifest.room_id != room_id for manifest in replay.manifests):
        raise ValueError(f'{event} room_id conflicts with retained manifests')
    flv_paths = record.get('flv_paths')
    if not isinstance(flv_paths, (list, tuple)) or any(
        not isinstance(path, str) or not path for path in flv_paths
    ):
        raise TypeError(f'{event} requires a list of non-empty flv_paths')
    if not flv_paths:
        raise ValueError(f'{event} requires at least one flv_path')
    normalized_flv_paths = [os.path.normpath(path) for path in flv_paths]
    if (
        len(set(flv_paths)) != len(flv_paths)
        or len(set(normalized_flv_paths)) != len(normalized_flv_paths)
    ):
        raise ValueError(f'{event} contains duplicate flv_paths')
    for path in flv_paths:
        _require_normalized_absolute_path(path, event, 'flv_path')
        if not path.lower().endswith('.flv'):
            raise ValueError(f'{event} flv_paths must end with .flv')

    raw_snapshot = record.get('snapshot')
    if not isinstance(raw_snapshot, Mapping):
        raise TypeError(f'{event} requires a snapshot object')
    raw_snapshot = dict(raw_snapshot)
    record['snapshot'] = raw_snapshot
    snapshot = {}
    normalized_snapshot_paths = set()
    for path, identity in raw_snapshot.items():
        if not isinstance(path, str) or not path:
            raise TypeError(f'{event} snapshot paths must be non-empty strings')
        normalized_path = os.path.normpath(path)
        if normalized_path in normalized_snapshot_paths:
            raise ValueError(
                f'{event} snapshot contains duplicate normalized paths'
            )
        normalized_snapshot_paths.add(normalized_path)
        _require_normalized_absolute_path(path, event, 'snapshot path')
        if not isinstance(identity, (list, tuple)) or len(identity) != 2:
            raise TypeError(
                f'{event} snapshot identities must be [size, mtime_ns] lists'
            )
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in identity
        ):
            raise TypeError(
                f'{event} snapshot size and mtime_ns must be '
                'non-negative integers'
            )
        snapshot[path] = tuple(identity)
    missing_identities = [path for path in flv_paths if path not in snapshot]
    if missing_identities:
        raise ValueError(
            f'{event} snapshot is missing flv_path identities: '
            + ', '.join(missing_identities)
        )
    allowed_snapshot_paths = set(flv_paths)
    allowed_snapshot_paths.update(
        os.path.splitext(path)[0] + '.xml' for path in flv_paths
    )
    unrelated_paths = sorted(set(snapshot).difference(allowed_snapshot_paths))
    if unrelated_paths:
        raise ValueError(
            f'{event} snapshot contains unrelated paths: '
            + ', '.join(unrelated_paths)
        )

    manifest = JournalManifest(
        manifest_id=record['manifest_id'],
        room_id=room_id,
        started_at=record['started_at'],
        settled_at=record['settled_at'],
        flv_paths=tuple(flv_paths),
        snapshot=snapshot,
    )
    manifests = list(replay.manifests)
    for index, existing in enumerate(manifests):
        if existing.manifest_id == manifest.manifest_id:
            existing_identity = replace(
                existing,
                completed=False,
                invalidated=False,
                invalidated_at=None,
                invalidation_reason=None,
                changed_paths=(),
                replacement_manifest_id=None,
            )
            if existing_identity != manifest:
                raise ValueError(
                    'cannot replace a manifest with different data'
                )
            manifest = replace(
                manifest,
                completed=existing.completed,
                invalidated=existing.invalidated,
                invalidated_at=existing.invalidated_at,
                invalidation_reason=existing.invalidation_reason,
                changed_paths=existing.changed_paths,
                replacement_manifest_id=existing.replacement_manifest_id,
            )
            manifests[index] = manifest
            break
    else:
        manifests.append(manifest)
    manifests.sort(key=lambda item: _parse_aware_instant(
        item.settled_at, 'settled_at', event
    ))
    return replace(replay, manifests=tuple(manifests))


def _reduce_manifest_completed(replay, record):
    event = 'session_manifest_completed'
    _validate_manifest_id(record, event)
    manifests = list(replay.manifests)
    for index, manifest in enumerate(manifests):
        if manifest.manifest_id == record['manifest_id']:
            if manifest.invalidated:
                raise ValueError(
                    'cannot complete an invalidated session manifest'
                )
            manifests[index] = replace(manifest, completed=True)
            return replace(replay, manifests=tuple(manifests))
    raise ValueError(
        'session_manifest_completed requires an existing ready manifest'
    )


def _validated_changed_paths(record, manifest, event):
    changed_paths = record.get('changed_paths')
    if not isinstance(changed_paths, (list, tuple)) or not changed_paths:
        raise ValueError(f'{event} requires non-empty changed_paths')
    if any(not isinstance(path, str) or not path for path in changed_paths):
        raise TypeError(f'{event} changed_paths must be non-empty strings')
    if len(set(changed_paths)) != len(changed_paths):
        raise ValueError(f'{event} contains duplicate changed_paths')
    for path in changed_paths:
        _require_normalized_absolute_path(path, event, 'changed_path')
    allowed_paths = set(manifest.flv_paths)
    allowed_paths.update(
        os.path.splitext(path)[0] + '.xml' for path in manifest.flv_paths
    )
    unrelated = set(changed_paths).difference(allowed_paths)
    if unrelated:
        raise ValueError(
            f'{event} changed_paths are outside the frozen manifest: '
            + ', '.join(sorted(unrelated))
        )
    return tuple(changed_paths)


def _reduce_manifest_changed(replay, record):
    event = 'session_manifest_changed'
    _validate_manifest_id(record, event)
    _require_non_empty_string(record, 'detected_at', event)
    _require_non_empty_string(record, 'reason', event)
    detected_at = _parse_aware_instant(
        record['detected_at'], 'detected_at', event
    )
    manifests = list(replay.manifests)
    for index, manifest in enumerate(manifests):
        if manifest.manifest_id != record['manifest_id']:
            continue
        changed_paths = _validated_changed_paths(record, manifest, event)
        if detected_at < _parse_aware_instant(
            manifest.settled_at, 'settled_at', event
        ):
            raise ValueError(
                f'{event} detected_at cannot precede manifest settlement'
            )
        signature = (
            record['detected_at'], record['reason'], changed_paths
        )
        existing_signature = (
            manifest.invalidated_at,
            manifest.invalidation_reason,
            manifest.changed_paths,
        )
        if manifest.invalidated:
            if signature != existing_signature:
                raise ValueError('conflicting invalidation for manifest')
            return replay
        if manifest.completed:
            raise ValueError('cannot invalidate a completed manifest')
        manifests[index] = replace(
            manifest,
            invalidated=True,
            invalidated_at=record['detected_at'],
            invalidation_reason=record['reason'],
            changed_paths=changed_paths,
        )
        pending = list(replay.pending_resettles)
        pending.append(JournalResettleRequest(
            source_manifest_id=manifest.manifest_id,
            settled_at=manifest.settled_at,
            detected_at=record['detected_at'],
            reason=record['reason'],
            changed_paths=changed_paths,
        ))
        pending.sort(key=lambda item: _parse_aware_instant(
            item.settled_at, 'settled_at', event
        ))
        return replace(
            replay,
            manifests=tuple(manifests),
            pending_resettles=tuple(pending),
        )
    raise ValueError(f'{event} requires an existing manifest')


def _reduce_resettle_started(replay, record):
    event = 'session_resettle_started'
    for name in ('source_manifest_id', 'replacement_manifest_id'):
        _require_non_empty_string(record, name, event)
    source_id = record['source_manifest_id']
    replacement_id = record['replacement_manifest_id']
    if source_id == replacement_id:
        raise ValueError(f'{event} replacement must use a new manifest ID')
    manifests = list(replay.manifests)
    source_index = next((
        index for index, item in enumerate(manifests)
        if item.manifest_id == source_id
    ), None)
    if source_index is None:
        raise ValueError(f'{event} requires an existing source manifest')
    source = manifests[source_index]
    if not source.invalidated:
        raise ValueError(f'{event} requires an invalidated source manifest')
    room_id = record.get('room_id')
    if room_id != source.room_id:
        raise ValueError(f'{event} room conflicts with the source manifest')
    try:
        state = SessionState(record.get('state'))
    except (TypeError, ValueError) as exception:
        raise TypeError(f'{event} has an invalid state') from exception
    if state not in {SessionState.RECORDING, SessionState.SETTLING}:
        raise ValueError(f'{event} state must be recording or settling')

    raw_snapshot = record.get('snapshot')
    if not isinstance(raw_snapshot, Mapping):
        raise TypeError(f'{event} requires a snapshot object')
    for path in raw_snapshot:
        if not isinstance(path, str) or not path:
            raise TypeError(f'{event} snapshot paths must be non-empty strings')
        _require_normalized_absolute_path(path, event, 'snapshot path')
    session_paths = record.get('session_paths')
    if not isinstance(session_paths, (list, tuple)):
        raise TypeError(f'{event} requires session_paths')
    replacement_started_at = _parse_aware_instant(
        record.get('started_at'), 'started_at', event
    )
    source_started_at = _parse_aware_instant(
        source.started_at, 'started_at', event
    )
    if replacement_started_at != source_started_at:
        raise ValueError(f'{event} must preserve the source started_at')
    quiet_since = _parse_aware_instant(
        record.get('quiet_since'), 'quiet_since', event
    )
    if quiet_since < replacement_started_at:
        raise ValueError(f'{event} quiet_since cannot precede started_at')

    session_record = {
        'state': state.value,
        'room_id': source.room_id,
        'session_id': replacement_id,
        'session_paths': tuple(session_paths),
        'snapshot': dict(raw_snapshot),
        'quiet_since': record.get('quiet_since'),
        'started_at': record.get('started_at'),
    }
    updated = _reduce_session_state(replay, session_record)

    if source.replacement_manifest_id is not None:
        if source.replacement_manifest_id != replacement_id:
            raise ValueError(f'{event} source manifest is already claimed')
        if updated.session != replay.session:
            raise ValueError(f'{event} has a conflicting duplicate claim')
        if any(
            item.source_manifest_id == source_id
            for item in replay.pending_resettles
        ):
            raise ValueError(f'{event} duplicate has inconsistent pending state')
        return replay

    if any(
        item.manifest_id == replacement_id
        or item.replacement_manifest_id == replacement_id
        for item in manifests
    ):
        raise ValueError(f'{event} replacement manifest ID is already used')
    if replay.session.state is not SessionState.WAITING:
        raise ValueError(f'{event} cannot replace an active session')
    if replay.session.room_id not in (None, source.room_id):
        raise ValueError(f'{event} room conflicts with the current session')
    if not any(
        item.source_manifest_id == source_id
        for item in replay.pending_resettles
    ):
        raise ValueError(f'{event} requires a pending resettle request')
    if not source.flv_paths:
        raise ValueError(f'{event} requires a current source FLV')

    current_snapshot = updated.session.snapshot
    expected_paths = set(source.flv_paths)
    for flv_path in source.flv_paths:
        if flv_path not in current_snapshot:
            raise ValueError(
                f'{event} current source FLV is missing: {flv_path}'
            )
        xml_path = os.path.splitext(flv_path)[0] + '.xml'
        if xml_path in current_snapshot:
            expected_paths.add(xml_path)
    if state is SessionState.RECORDING:
        expected_paths.update(
            path for path, identity in current_snapshot.items()
            if path.lower().endswith(('.flv', '.xml'))
            and replay.session.snapshot.get(path) != identity
        )
    if set(session_paths) != expected_paths:
        raise ValueError(
            f'{event} session_paths do not match the claimed recording paths'
        )
    if len(session_paths) != len(expected_paths):
        raise ValueError(f'{event} contains duplicate session_paths')

    manifests[source_index] = replace(
        source, replacement_manifest_id=replacement_id
    )
    pending = tuple(
        item for item in replay.pending_resettles
        if item.source_manifest_id != source_id
    )
    return replace(
        updated,
        manifests=tuple(manifests),
        pending_resettles=pending,
    )


def _validate_delete_intent_record(record):
    event = 'source_delete_intent'
    for name in ('fingerprint', 'original_path', 'quarantine_path', 'reason'):
        _require_non_empty_string(record, name, event)
    original_path = record['original_path']
    if (
        not os.path.isabs(original_path)
        or canonical_source_path(original_path) != original_path
    ):
        raise ValueError(f'{event} original_path must be normalized absolute')
    quarantine_path = record['quarantine_path']
    quarantine_parts = Path(quarantine_path).parts
    if (
        os.path.isabs(quarantine_path)
        or os.path.normpath(quarantine_path) != quarantine_path
        or len(quarantine_parts) != 2
        or quarantine_parts[0] != '.bililive-cleanup-quarantine'
        or quarantine_parts[1] in ('', '.', '..')
    ):
        raise ValueError(f'{event} requires a safe quarantine_path')
    for name in ('dev', 'ino', 'size', 'mtime_ns'):
        value = record.get(name)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise TypeError(f'{event} requires non-negative integer {name}')


def _owned_source_paths(state):
    owned = {
        canonical_source_path(path)
        for path in (state.file, state.xml_file)
        if path is not None
    }
    if state.file is not None and state.event != 'baseline':
        owned.add(canonical_source_path(
            os.path.splitext(state.file)[0] + '.xml'
        ))
    deleted = {
        canonical_source_path(path) for path in state.deleted_paths
    }
    return owned - deleted


def _source_path_owners(replay, path):
    canonical = canonical_source_path(path)
    return {
        fingerprint
        for fingerprint, state in replay.files.items()
        if canonical in _owned_source_paths(state)
    }


def _canonical_record_paths(values):
    return {
        canonical_source_path(path) for path in values
        if isinstance(path, str) and path
    }


def _new_record_claims(replay, record):
    event = record['event']
    if event in {'session_state', 'session_resettle_started'}:
        claimed = _canonical_record_paths(record.get('session_paths', ()))
        claimed.update(_canonical_record_paths(record.get('snapshot', {})))
        return claimed
    if event == 'session_manifest_ready':
        claimed = _canonical_record_paths(record.get('flv_paths', ()))
        claimed.update(_canonical_record_paths(record.get('snapshot', {})))
        return claimed
    if event == 'session_manifest_changed':
        return _canonical_record_paths(record.get('changed_paths', ()))
    if event in _INITIAL_FILE_EVENTS:
        return _canonical_record_paths(
            (record.get('file'), record.get('xml_file'))
        )
    return set()


def _validate_pending_delete_leases(replay, record):
    leased = {
        intent.original_path for intent in replay.pending_deletions
        if not intent.source_deleted
    }
    if leased.intersection(_new_record_claims(replay, record)):
        raise ValueError('journal event conflicts with a pending deletion lease')


def _reduce_delete_intent(replay, record):
    _validate_delete_intent_record(record)
    fingerprint = record['fingerprint']
    state = replay.files.get(fingerprint)
    if state is None:
        raise ValueError('source_delete_intent requires an existing file state')
    original_path = record['original_path']
    if _source_path_owners(replay, original_path) != {fingerprint}:
        raise ValueError(
            'source_delete_intent path must be owned by one fingerprint'
        )
    if original_path in state.deleted_paths:
        raise ValueError('source_delete_intent path is already deleted')

    intent = JournalDeleteIntent(
        fingerprint=fingerprint,
        original_path=original_path,
        quarantine_path=record['quarantine_path'],
        dev=record['dev'],
        ino=record['ino'],
        size=record['size'],
        mtime_ns=record['mtime_ns'],
        reason=record['reason'],
    )
    for existing in replay.pending_deletions:
        if existing == intent:
            return replay
        if existing.quarantine_path == intent.quarantine_path:
            raise ValueError('source_delete_intent quarantine_path is not unique')
        if (
            existing.fingerprint == fingerprint
            and existing.original_path == original_path
        ):
            raise ValueError('source_delete_intent conflicts with pending intent')
    return replace(
        replay,
        pending_deletions=replay.pending_deletions + (intent,),
    )


def _validate_quarantine_removed_record(record):
    event = 'quarantine_removed'
    for name in ('fingerprint', 'original_path', 'quarantine_path'):
        _require_non_empty_string(record, name, event)
    if canonical_source_path(record['original_path']) != record['original_path']:
        raise ValueError(
            'quarantine_removed original_path must be normalized absolute'
        )


def _reduce_quarantine_removed(replay, record):
    _validate_quarantine_removed_record(record)
    matches = tuple(
        intent for intent in replay.pending_deletions
        if (
            intent.fingerprint == record['fingerprint']
            and intent.original_path == record['original_path']
            and intent.quarantine_path == record['quarantine_path']
        )
    )
    if len(matches) != 1:
        raise ValueError('quarantine_removed requires one pending intent')
    if not matches[0].source_deleted:
        raise ValueError('quarantine_removed requires durable source_deleted')
    return replace(
        replay,
        pending_deletions=tuple(
            intent for intent in replay.pending_deletions
            if intent is not matches[0]
        ),
    )


def _validate_delete_aborted_record(record):
    event = 'source_delete_aborted'
    for name in ('fingerprint', 'original_path', 'quarantine_path', 'reason'):
        _require_non_empty_string(record, name, event)
    if canonical_source_path(record['original_path']) != record['original_path']:
        raise ValueError(f'{event} original_path must be normalized absolute')
    recovery_path = record.get('recovery_path')
    if recovery_path is not None:
        _require_non_empty_string(record, 'recovery_path', event)
        if canonical_source_path(recovery_path) != recovery_path:
            raise ValueError(f'{event} recovery_path must be normalized absolute')
        if (
            Path(recovery_path).parent != Path(record['original_path']).parent
            or Path(recovery_path).suffix.lower() != '.bin'
        ):
            raise ValueError(
                f'{event} recovery_path must be a .bin in the source parent'
            )


def _reduce_delete_aborted(replay, record):
    _validate_delete_aborted_record(record)
    abort = JournalDeleteAbort(
        fingerprint=record['fingerprint'],
        original_path=record['original_path'],
        quarantine_path=record['quarantine_path'],
        reason=record['reason'],
        recovery_path=record.get('recovery_path'),
    )
    if abort in replay.deletion_aborts:
        return replay
    if any(
        item.fingerprint == abort.fingerprint
        and item.original_path == abort.original_path
        and item.quarantine_path == abort.quarantine_path
        for item in replay.deletion_aborts
    ):
        raise ValueError('source_delete_aborted conflicts with durable abort')
    matches = tuple(
        intent for intent in replay.pending_deletions
        if intent.fingerprint == abort.fingerprint
        and intent.original_path == abort.original_path
        and intent.quarantine_path == abort.quarantine_path
    )
    if len(matches) != 1 or matches[0].source_deleted:
        raise ValueError('source_delete_aborted requires one pre-delete intent')
    files = dict(replay.files)
    state = files.get(abort.fingerprint)
    if state is None:
        raise ValueError('source_delete_aborted requires an existing file state')
    deleted_paths = tuple(
        canonical_source_path(path) for path in state.deleted_paths
    )
    if abort.original_path not in deleted_paths:
        files[abort.fingerprint] = replace(
            state, deleted_paths=deleted_paths + (abort.original_path,)
        )
    return replace(
        replay,
        files=files,
        pending_deletions=tuple(
            intent for intent in replay.pending_deletions
            if intent is not matches[0]
        ),
        deletion_aborts=replay.deletion_aborts + (abort,),
    )


_CONTROL_REDUCERS = {
    'initialized': _reduce_initialized,
    'session_state': _reduce_session_state,
    'session_manifest_ready': _reduce_manifest_ready,
    'session_manifest_completed': _reduce_manifest_completed,
    'session_manifest_changed': _reduce_manifest_changed,
    'session_resettle_started': _reduce_resettle_started,
    'source_delete_intent': _reduce_delete_intent,
    'quarantine_removed': _reduce_quarantine_removed,
    'source_delete_aborted': _reduce_delete_aborted,
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
    if event == 'session_manifest_changed':
        _validate_manifest_id(record, event)
        return
    if event == 'session_resettle_started':
        for name in ('source_manifest_id', 'replacement_manifest_id'):
            _require_non_empty_string(record, name, event)
        return
    if event == 'source_delete_intent':
        _validate_delete_intent_record(record)
        return
    if event == 'quarantine_removed':
        _validate_quarantine_removed_record(record)
        return
    if event == 'source_delete_aborted':
        _validate_delete_aborted_record(record)
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
        self._file = None
        self._entered = False
        lock_file = self.path.open('a+b')
        locking = False
        try:
            if not lock_file_existed:
                lock_file.flush()
                os.fsync(lock_file.fileno())
                _fsync_directory(self.state_dir)
            locking = True
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BaseException as exception:
            lock_file.close()
            if (
                locking
                and isinstance(exception, OSError)
                and exception.errno in (errno.EACCES, errno.EAGAIN)
            ):
                raise AlreadyRunningError(
                    f'Bililive monitor is already running: {self.path}'
                ) from exception
            raise
        self._file = lock_file

    def close(self):
        lock_file = self._file
        if lock_file is None:
            return
        self._file = None
        self._entered = False
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        finally:
            lock_file.close()

    def __enter__(self):
        if self._file is None:
            raise RuntimeError('process lock is closed')
        if self._entered:
            raise RuntimeError('process lock is already entered')
        self._entered = True
        return self

    def __exit__(self, exception_type, exception, traceback):
        self.close()


@dataclass(frozen=True)
class _ReplayState:
    files: dict[str, JournalFileState]
    manifests: tuple[JournalManifest, ...]
    session: JournalSessionState
    initialized: bool
    pending_resettles: tuple[JournalResettleRequest, ...]
    pending_deletions: tuple[JournalDeleteIntent, ...]
    deletion_aborts: tuple[JournalDeleteAbort, ...]


def _empty_replay():
    return _ReplayState(
        files={},
        manifests=(),
        session=JournalSessionState(
            state=SessionState.BASELINING,
            room_id=None,
            session_id=None,
            session_paths=(),
            snapshot={},
            quiet_since=None,
            started_at=None,
        ),
        initialized=False,
        pending_resettles=(),
        pending_deletions=(),
        deletion_aborts=(),
    )


def _public_replay(replay, journal_version=0):
    return JournalReplay(
        files=replay.files,
        manifests=replay.manifests,
        session=replay.session,
        initialized=replay.initialized,
        pending_resettles=replay.pending_resettles,
        pending_deletions=replay.pending_deletions,
        journal_version=journal_version,
        deletion_aborts=replay.deletion_aborts,
    )


class JsonlJournal:
    def __init__(self, path):
        self.path = Path(path).resolve()
        self._mutex = _shared_journal_lock(self.path)

    def append(self, event, **fields):
        record = dict(fields, event=event)
        with self._mutex:
            _validate_append_record(record)
            journal_existed = self.path.exists()
            existing_payload = self.path.read_bytes() if journal_existed else b''
            replay, torn_offset, needs_separator = self._replay_payload(
                existing_payload
            )
            journal_version = (
                torn_offset if torn_offset is not None
                else len(existing_payload)
            )
            if event in _DELETE_TRANSACTION_EVENTS and (
                event == 'source_delete_intent'
                or 'expected_journal_version' in record
            ):
                expected = record.get('expected_journal_version')
                if (
                    isinstance(expected, bool)
                    or not isinstance(expected, int)
                    or expected < 0
                ):
                    raise TypeError(
                        f'{event} requires a non-negative '
                        'expected_journal_version'
                    )
                if expected != journal_version:
                    raise ValueError(f'{event} journal version changed')
            else:
                _validate_pending_delete_leases(replay, record)
            updated = self._reduce(replay, record)
            if updated is replay:
                return journal_version
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
                journal_version = journal_file.tell()
            if not journal_existed:
                _fsync_directory(self.path.parent)
            return journal_version

    def replay(self):
        with self._mutex:
            if not self.path.exists():
                return _public_replay(_empty_replay())
            payload = self.path.read_bytes()
            replay, torn_offset, _ = self._replay_payload(payload)
            journal_version = (
                torn_offset if torn_offset is not None else len(payload)
            )
            return _public_replay(replay, journal_version)

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
        same_generation = bool(
            existing is not None
            and record.get('manifest_id', existing.manifest_id)
            == existing.manifest_id
        )
        controlled_identity_migration = bool(
            existing is not None
            and existing.manifest_id is not None
            and record.get('manifest_id', existing.manifest_id)
            != existing.manifest_id
        )
        if (
            event in _INITIAL_FILE_EVENTS
            and existing is not None
            and not controlled_identity_migration
        ):
            for field_name in ('source_size', 'source_mtime_ns'):
                old_value = getattr(existing, field_name)
                new_value = record.get(field_name, old_value)
                if (
                    old_value is not None
                    and new_value != old_value
                ):
                    raise ValueError(
                        'classification cannot change source identity '
                        'within one manifest generation'
                    )
        if (
            existing is not None
            and event in _INITIAL_FILE_EVENTS
            and same_generation
            and _has_publication_lifecycle(existing)
        ):
            raise ValueError(
                'publication lifecycle cannot be reclassified within the '
                'same generation'
            )
        if (
            event == 'video_uploaded'
            and existing.video_id == record['video_id']
        ):
            return replay
        if (
            event == 'caption_source_frozen'
            and existing.caption_source_xml_size is not None
            and existing.caption_source_xml_mtime_ns is not None
        ):
            return replay
        updates = _file_event_updates(record, event, existing)
        state_event = existing.event if event == 'source_deleted' else event
        if existing is None:
            state = JournalFileState(
                fingerprint=fingerprint, event=state_event, **updates
            )
        else:
            state = replace(existing, event=state_event, **updates)
        caption_changed = _validate_file_binding(
            replay, state, existing, event
        )
        if (
            existing is not None
            and existing.manifest_id != state.manifest_id
        ):
            if _has_publication_lifecycle(existing):
                state = _migrate_publication_state(existing, state)
            if caption_changed:
                remote_caption_evidence = (
                    existing.caption_uploaded
                    or existing.caption_refresh_required
                )
                state = replace(
                    state,
                    caption_uploaded=False,
                    caption_refresh_required=remote_caption_evidence,
                    caption_track_id=(
                        existing.caption_track_id
                        if remote_caption_evidence else None
                    ),
                    caption_status='pending',
                )
            else:
                state = replace(
                    state, caption_status=existing.caption_status
                )
        files = dict(replay.files)
        files[fingerprint] = state
        replay = replace(replay, files=files)
        if event == 'source_deleted':
            deleted_path = canonical_source_path(record['path'])
            matching_intents = tuple(
                intent for intent in replay.pending_deletions
                if (
                    intent.fingerprint == fingerprint
                    and intent.original_path == deleted_path
                )
            )
            if len(matching_intents) > 1:
                raise ValueError('source_deleted has ambiguous pending intents')
            if matching_intents:
                intent = matching_intents[0]
                if intent.reason != record['reason']:
                    raise ValueError('source_deleted reason conflicts with intent')
                return replace(
                    replay,
                    pending_deletions=tuple(
                        replace(item, source_deleted=True)
                        if item is intent else item
                        for item in replay.pending_deletions
                    ),
                )
        return replay

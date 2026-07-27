import errno
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path

import pytest

import recorder.bililive.journal as journal_module
from recorder.bililive.journal import JournalCorruptError, JsonlJournal
from recorder.bililive.journal import (
    AlreadyRunningError,
    ProcessLock,
    baseline_fingerprint,
)
from recorder.bililive.models import (
    JournalDeleteIntent,
    JournalFileState,
    JournalManifest,
    JournalReplay,
    JournalResettleRequest,
    JournalSessionState,
    RoomState,
    SessionState,
)


DELETE_IDENTITY = {
    'dev': 10,
    'ino': 20,
    'size': 30,
    'mtime_ns': 40,
}


def append_delete_intent(journal, **overrides):
    fields = {
        'fingerprint': 'baseline:1',
        'original_path': '/video.flv',
        'quarantine_path': '.bililive-cleanup-quarantine/delete-1',
        'reason': 'disk pressure',
        **DELETE_IDENTITY,
    }
    fields.update(overrides)
    journal.append('source_delete_intent', **fields)


def test_delete_intent_replays_each_durable_phase_immutably(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('baseline', fingerprint='baseline:1', file='/video.flv')

    append_delete_intent(journal)

    replay = journal.replay()
    assert replay.pending_deletions == (JournalDeleteIntent(
        fingerprint='baseline:1',
        original_path='/video.flv',
        quarantine_path='.bililive-cleanup-quarantine/delete-1',
        dev=10,
        ino=20,
        size=30,
        mtime_ns=40,
        reason='disk pressure',
        source_deleted=False,
    ),)
    with pytest.raises(FrozenInstanceError):
        replay.pending_deletions[0].source_deleted = True

    journal.append(
        'source_deleted', fingerprint='baseline:1', path='/video.flv',
        reason='disk pressure',
    )

    replay = journal.replay()
    assert replay.pending_deletions[0].source_deleted is True
    assert replay.files['baseline:1'].deleted_paths == ('/video.flv',)

    journal.append(
        'quarantine_removed', fingerprint='baseline:1',
        original_path='/video.flv',
        quarantine_path='.bililive-cleanup-quarantine/delete-1',
    )

    assert journal.replay().pending_deletions == ()


@pytest.mark.parametrize(
    ('field', 'value'),
    [
        ('original_path', 'relative.flv'),
        ('quarantine_path', '/absolute/quarantine'),
        ('quarantine_path', '../escape'),
        ('dev', True),
        ('ino', -1),
        ('size', '30'),
        ('mtime_ns', None),
    ],
)
def test_delete_intent_rejects_unsafe_paths_and_identity(
    tmp_path, field, value
):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('baseline', fingerprint='baseline:1', file='/video.flv')
    before = journal.path.read_bytes()

    with pytest.raises((TypeError, ValueError)):
        append_delete_intent(journal, **{field: value})

    assert journal.path.read_bytes() == before


def test_delete_intent_requires_exact_state_path_ownership(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('baseline', fingerprint='baseline:1', file='/video.flv')

    with pytest.raises(ValueError, match='owned'):
        append_delete_intent(journal, original_path='/other.flv')


def test_delete_intent_quarantine_name_is_unique(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('baseline', fingerprint='baseline:1', file='/video.flv')
    journal.append('baseline', fingerprint='baseline:2', file='/other.flv')
    append_delete_intent(journal)

    with pytest.raises(ValueError, match='quarantine'):
        append_delete_intent(
            journal, fingerprint='baseline:2', original_path='/other.flv'
        )


def test_quarantine_removed_requires_durable_source_deleted(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('baseline', fingerprint='baseline:1', file='/video.flv')
    append_delete_intent(journal)

    with pytest.raises(ValueError, match='source_deleted'):
        journal.append(
            'quarantine_removed', fingerprint='baseline:1',
            original_path='/video.flv',
            quarantine_path='.bililive-cleanup-quarantine/delete-1',
        )


def test_journal_replays_cumulative_latest_file_state(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append(
        'file_ready',
        fingerprint='fp1',
        file='/video.flv',
        title='first title',
    )
    journal.append('video_uploaded', fingerprint='fp1', video_id='yt123')

    state = journal.replay().files['fp1']

    assert state.event == 'video_uploaded'
    assert state.file == '/video.flv'
    assert state.title == 'first title'
    assert state.video_id == 'yt123'


def test_append_writes_one_durable_compact_utf8_line(tmp_path, monkeypatch):
    fsync_calls = []
    monkeypatch.setattr(
        journal_module.os,
        'fsync',
        lambda file_descriptor: fsync_calls.append(file_descriptor),
    )
    path = tmp_path / 'nested' / 'state.jsonl'

    JsonlJournal(path).append(
        'baseline', fingerprint='baseline:1', file='/録画.flv'
    )

    payload = path.read_bytes()
    assert payload.endswith(b'\n')
    assert payload.count(b'\n') == 1
    assert b'/\xe9\x8c\xb2\xe7\x94\xbb.flv' in payload
    assert b': ' not in payload
    record = json.loads(payload)
    recorded_at = datetime.fromisoformat(record.pop('recorded_at'))
    assert recorded_at.tzinfo is not None
    assert recorded_at.utcoffset() == timezone.utc.utcoffset(recorded_at)
    assert record == {
        'event': 'baseline',
        'fingerprint': 'baseline:1',
        'file': '/録画.flv',
    }
    assert fsync_calls


def test_missing_or_empty_journal_has_conservative_defaults(tmp_path):
    missing = JsonlJournal(tmp_path / 'missing.jsonl').replay()
    empty_path = tmp_path / 'empty.jsonl'
    empty_path.touch()
    empty = JsonlJournal(empty_path).replay()

    for replay in (missing, empty):
        assert replay.initialized is False
        assert replay.files == {}
        assert replay.manifests == ()
        assert replay.session.state is SessionState.BASELINING
        assert replay.session.room_id is None
        assert replay.session.session_id is None
        assert replay.session.session_paths == ()
        assert replay.session.snapshot == {}


@pytest.mark.parametrize('fragment', [b'{"event":"baseline"', b'\xff\xfe'])
def test_replay_ignores_only_invalid_unterminated_final_fragment(tmp_path, fragment):
    path = tmp_path / 'state.jsonl'
    path.write_bytes(
        b'{"event":"baseline","fingerprint":"baseline:1","file":"/a.flv"}\n'
        + fragment
    )

    replay = JsonlJournal(path).replay()

    assert set(replay.files) == {'baseline:1'}


def test_replay_rejects_valid_unterminated_event_missing_required_fields(tmp_path):
    path = tmp_path / 'state.jsonl'
    path.write_bytes(b'{"event":"video_uploaded","video_id":"yt123"}')

    with pytest.raises(JournalCorruptError, match='line 1'):
        JsonlJournal(path).replay()


@pytest.mark.parametrize(
    'payload, line_number',
    [
        (
            b'{"event":"baseline","fingerprint":"baseline:1","file":"/a.flv"}\n'
            b'not-json\n'
            b'{"event":"baseline","fingerprint":"baseline:2","file":"/b.flv"}\n',
            2,
        ),
        (b'not-json\n', 1),
        (b'\xff\xfe\n', 1),
    ],
)
def test_replay_rejects_corrupt_complete_lines(tmp_path, payload, line_number):
    path = tmp_path / 'state.jsonl'
    path.write_bytes(payload)

    with pytest.raises(JournalCorruptError, match=f'line {line_number}'):
        JsonlJournal(path).replay()


def test_room_state_and_replayed_models_are_immutable(tmp_path):
    assert RoomState(recording=False, streaming=True).active is True
    assert RoomState(recording=False, streaming=False).active is False
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('baseline', fingerprint='baseline:1', file='/video.flv')
    state = journal.replay().files['baseline:1']

    with pytest.raises(FrozenInstanceError):
        state.event = 'changed'


@pytest.mark.parametrize(
    ('first_event', 'second_event'),
    [
        ('file_ready', 'ignored_tiny'),
        ('ignored_tiny', 'file_ready'),
    ],
)
def test_append_rejects_different_fingerprint_for_manifest_file_binding(
    tmp_path, first_event, second_event
):
    journal = JsonlJournal(tmp_path / 'state.jsonl')

    def append_classification(event, fingerprint):
        fields = {
            'fingerprint': fingerprint,
            'manifest_id': 'session-1',
            'file': '/recording/video.flv',
        }
        if event == 'ignored_tiny':
            fields['reason'] = 'too small'
        journal.append(event, **fields)

    append_classification(first_event, 'fp-first')
    original = journal.path.read_bytes()

    with pytest.raises(ValueError, match='manifest/file binding'):
        append_classification(second_event, 'fp-second')

    assert journal.path.read_bytes() == original
    assert set(journal.replay().files) == {'fp-first'}


def test_raw_replay_rejects_duplicate_manifest_file_fingerprint_binding(
    tmp_path,
):
    path = tmp_path / 'state.jsonl'
    records = [
        {
            'event': 'file_ready',
            'fingerprint': 'fp-first',
            'manifest_id': 'session-1',
            'file': '/recording/video.flv',
        },
        {
            'event': 'file_ready',
            'fingerprint': 'fp-second',
            'manifest_id': 'session-1',
            'file': '/recording/video.flv',
        },
    ]
    path.write_text(
        ''.join(json.dumps(record) + '\n' for record in records),
        encoding='utf8',
    )

    with pytest.raises(
        JournalCorruptError, match='line 2.*manifest/file binding'
    ):
        JsonlJournal(path).replay()


def test_exact_duplicate_classification_keeps_same_fingerprint_binding(
    tmp_path,
):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    fields = {
        'fingerprint': 'fp1',
        'manifest_id': 'session-1',
        'file': '/recording/video.flv',
        'caption_status': 'pending',
    }

    journal.append('file_ready', **fields)
    journal.append('file_ready', **fields)
    journal.append('video_uploaded', fingerprint='fp1', video_id='yt123')

    state = journal.replay().files['fp1']
    assert state.manifest_id == 'session-1'
    assert state.file == '/recording/video.flv'
    assert state.video_id == 'yt123'


@pytest.mark.parametrize(
    'invalid_migration',
    [
        'direct',
        'unclaimed',
        'not-ready',
        'wrong-path',
        'cross-room',
        'conflicting-identity',
    ],
)
def test_raw_replay_rejects_invalid_manifest_migration(
    tmp_path, invalid_migration
):
    path = tmp_path / 'state.jsonl'
    journal = JsonlJournal(path)
    video = '/recording/video.flv'
    xml = '/recording/video.xml'
    journal.append('initialized')
    journal.append(
        'session_state',
        room_id=123,
        state='waiting',
        session_id=None,
        session_paths=(),
        snapshot={video: (100, 1), xml: (10, 1)},
        quiet_since=None,
        started_at=None,
    )
    journal.append(
        'session_manifest_ready',
        manifest_id='old-session',
        room_id=123,
        started_at='2026-07-27T08:00:00+00:00',
        settled_at='2026-07-27T12:00:00+00:00',
        flv_paths=(video,),
        snapshot={video: (100, 1), xml: (10, 1)},
    )
    journal.append(
        'file_ready',
        fingerprint='fp1',
        manifest_id='old-session',
        file=video,
        xml_file=xml,
    )

    if invalid_migration != 'direct':
        journal.append(
            'session_manifest_changed',
            manifest_id='old-session',
            detected_at='2026-07-27T12:05:00+00:00',
            reason='XML changed',
            changed_paths=(xml,),
        )
    if invalid_migration not in {'direct', 'unclaimed'}:
        journal.append(
            'session_resettle_started',
            source_manifest_id='old-session',
            replacement_manifest_id='replacement-session',
            room_id=123,
            state='settling',
            session_paths=(video, xml),
            snapshot={video: (100, 1), xml: (20, 2)},
            quiet_since='2026-07-27T12:10:00+00:00',
            started_at='2026-07-27T08:00:00+00:00',
        )

    migration_file = video
    target_snapshot = {video: (100, 1), xml: (20, 2)}
    if invalid_migration == 'wrong-path':
        migration_file = '/recording/other.flv'
        target_snapshot = {migration_file: (100, 1)}
    elif invalid_migration == 'conflicting-identity':
        target_snapshot = {video: (101, 2), xml: (20, 2)}

    target_record = {
        'event': 'session_manifest_ready',
        'manifest_id': 'replacement-session',
        'room_id': 456 if invalid_migration == 'cross-room' else 123,
        'started_at': '2026-07-27T08:00:00+00:00',
        'settled_at': '2026-07-27T12:40:00+00:00',
        'flv_paths': [migration_file],
        'snapshot': target_snapshot,
    }
    migration_record = {
        'event': 'file_ready',
        'fingerprint': 'fp1',
        'manifest_id': 'replacement-session',
        'file': migration_file,
        'xml_file': str(Path(migration_file).with_suffix('.xml')),
    }
    raw_records = []
    if invalid_migration != 'not-ready':
        raw_records.append(target_record)
    raw_records.append(migration_record)
    path.write_text(
        path.read_text(encoding='utf8')
        + ''.join(json.dumps(record) + '\n' for record in raw_records),
        encoding='utf8',
    )

    with pytest.raises(JournalCorruptError):
        journal.replay()


def test_multi_file_migration_reuses_only_unchanged_flv_binding(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    a_flv = '/recording/a.flv'
    a_xml = '/recording/a.xml'
    b_flv = '/recording/b.flv'
    b_xml = '/recording/b.xml'
    old_snapshot = {
        a_flv: (100, 1), a_xml: (10, 1),
        b_flv: (200, 1), b_xml: (20, 1),
    }
    replacement_snapshot = {
        a_flv: (150, 2), a_xml: (10, 1),
        b_flv: (200, 1), b_xml: (20, 1),
    }
    final_snapshot = {
        a_flv: (175, 3), a_xml: (10, 1),
        b_flv: (200, 1), b_xml: (20, 1),
    }
    journal.append('initialized')
    journal.append(
        'session_state',
        room_id=123,
        state='waiting',
        session_id=None,
        session_paths=(),
        snapshot=old_snapshot,
        quiet_since=None,
        started_at=None,
    )
    journal.append(
        'session_manifest_ready',
        manifest_id='old-session',
        room_id=123,
        started_at='2026-07-27T08:00:00+00:00',
        settled_at='2026-07-27T12:00:00+00:00',
        flv_paths=(a_flv, b_flv),
        snapshot=old_snapshot,
    )
    for fingerprint, flv, xml, video_id in (
        ('fp-a-old', a_flv, a_xml, 'yt-a-old'),
        ('fp-b', b_flv, b_xml, 'yt-b-old'),
    ):
        journal.append(
            'file_ready',
            fingerprint=fingerprint,
            manifest_id='old-session',
            file=flv,
            xml_file=xml,
            caption_status='uploaded',
        )
        journal.append(
            'video_uploaded', fingerprint=fingerprint, video_id=video_id
        )
        journal.append('caption_uploaded', fingerprint=fingerprint)
        journal.append('playlist_inserted', fingerprint=fingerprint)
        journal.append('youtube_processed', fingerprint=fingerprint)
    journal.append(
        'session_manifest_changed',
        manifest_id='old-session',
        detected_at='2026-07-27T12:05:00+00:00',
        reason='A FLV changed',
        changed_paths=(a_flv,),
    )
    journal.append(
        'session_resettle_started',
        source_manifest_id='old-session',
        replacement_manifest_id='replacement-session',
        room_id=123,
        state='settling',
        session_paths=(a_flv, a_xml, b_flv, b_xml),
        snapshot=replacement_snapshot,
        quiet_since='2026-07-27T12:10:00+00:00',
        started_at='2026-07-27T08:00:00+00:00',
    )
    journal.append(
        'session_manifest_ready',
        manifest_id='replacement-session',
        room_id=123,
        started_at='2026-07-27T08:00:00+00:00',
        settled_at='2026-07-27T12:40:00+00:00',
        flv_paths=(a_flv, b_flv),
        snapshot=replacement_snapshot,
    )
    journal.append(
        'session_manifest_changed',
        manifest_id='replacement-session',
        detected_at='2026-07-27T12:45:00+00:00',
        reason='A FLV changed again',
        changed_paths=(a_flv,),
    )
    journal.append(
        'session_state', room_id=123, state='waiting', session_id=None,
        session_paths=(), snapshot=final_snapshot, quiet_since=None,
        started_at=None,
    )
    journal.append(
        'session_resettle_started',
        source_manifest_id='replacement-session',
        replacement_manifest_id='final-session',
        room_id=123,
        state='settling',
        session_paths=(a_flv, a_xml, b_flv, b_xml),
        snapshot=final_snapshot,
        quiet_since='2026-07-27T12:50:00+00:00',
        started_at='2026-07-27T08:00:00+00:00',
    )
    journal.append(
        'session_manifest_ready',
        manifest_id='final-session',
        room_id=123,
        started_at='2026-07-27T08:00:00+00:00',
        settled_at='2026-07-27T13:20:00+00:00',
        flv_paths=(a_flv, b_flv),
        snapshot=final_snapshot,
    )

    journal.append(
        'file_ready',
        fingerprint='fp-b',
        manifest_id='final-session',
        file=b_flv,
        xml_file=b_xml,
        caption_status='pending',
    )

    migrated_b = journal.replay().files['fp-b']
    assert migrated_b.manifest_id == 'final-session'
    assert migrated_b.video_id == 'yt-b-old'
    assert migrated_b.caption_uploaded is True
    before_rejected_a = journal.path.read_bytes()
    with pytest.raises(ValueError, match='frozen FLV identity'):
        journal.append(
            'file_ready',
            fingerprint='fp-a-old',
            manifest_id='final-session',
            file=a_flv,
            xml_file=a_xml,
        )
    assert journal.path.read_bytes() == before_rejected_a
    assert journal.replay().files['fp-a-old'].manifest_id == 'old-session'


def _append_single_file_replacement(
    journal, *, fingerprint='fp1', initial_event='file_ready',
    replacement_event='file_ready', old_xml=(10, 1), new_xml=(10, 1),
    publication_events=(),
):
    video = '/recording/video.flv'
    xml = '/recording/video.xml'
    old_snapshot = {video: (100, 1), xml: old_xml}
    new_snapshot = {video: (100, 1), xml: new_xml}
    journal.append('initialized')
    journal.append(
        'session_state', room_id=123, state='waiting', session_id=None,
        session_paths=(), snapshot=old_snapshot, quiet_since=None,
        started_at=None,
    )
    journal.append(
        'session_manifest_ready', manifest_id='old-session', room_id=123,
        started_at='2026-07-27T08:00:00+00:00',
        settled_at='2026-07-27T12:00:00+00:00', flv_paths=(video,),
        snapshot=old_snapshot,
    )
    classification = {
        'fingerprint': fingerprint, 'manifest_id': 'old-session',
        'file': video, 'xml_file': xml, 'start_time':
        '2026-07-27T08:00:00+00:00', 'duration': 3600,
    }
    if initial_event.startswith('ignored_'):
        classification['reason'] = 'old classification'
    journal.append(initial_event, **classification)
    for publication_event, fields in publication_events:
        journal.append(publication_event, fingerprint=fingerprint, **fields)
    journal.append(
        'session_manifest_changed', manifest_id='old-session',
        detected_at='2026-07-27T12:05:00+00:00', reason='replacement',
        changed_paths=(xml,),
    )
    journal.append(
        'session_resettle_started', source_manifest_id='old-session',
        replacement_manifest_id='replacement-session', room_id=123,
        state='settling', session_paths=(video, xml), snapshot=new_snapshot,
        quiet_since='2026-07-27T12:10:00+00:00',
        started_at='2026-07-27T08:00:00+00:00',
    )
    journal.append(
        'session_manifest_ready', manifest_id='replacement-session',
        room_id=123, started_at='2026-07-27T08:00:00+00:00',
        settled_at='2026-07-27T12:40:00+00:00', flv_paths=(video,),
        snapshot=new_snapshot,
    )
    replacement = dict(classification, manifest_id='replacement-session')
    if replacement_event.startswith('ignored_'):
        replacement['reason'] = 'replacement classification'
    journal.append(replacement_event, **replacement)
    return journal.replay().files[fingerprint]


def test_manifest_migration_preserves_unresolved_upload_lifecycle(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    video = '/recording/video.flv'
    xml = '/recording/video.xml'
    snapshot = {video: (100, 1), xml: (10, 1)}
    journal.append('initialized')
    journal.append(
        'session_state', room_id=123, state='waiting', session_id=None,
        session_paths=(), snapshot=snapshot, quiet_since=None,
        started_at=None,
    )
    journal.append(
        'session_manifest_ready', manifest_id='old-session', room_id=123,
        started_at='2026-07-27T08:00:00+00:00',
        settled_at='2026-07-27T12:00:00+00:00', flv_paths=(video,),
        snapshot=snapshot,
    )
    journal.append(
        'file_ready', fingerprint='fp1', manifest_id='old-session',
        file=video, xml_file=xml, start_time='2026-07-27T08:00:00+00:00',
        duration=3600,
    )
    journal.append(
        'upload_started', fingerprint='fp1', file=video, xml_file=xml,
        title='title', duration=3600,
        description_fingerprint='description',
        upload_started_at='2026-07-27T12:01:00+00:00', attempt=2,
    )
    journal.append(
        'session_manifest_changed', manifest_id='old-session',
        detected_at='2026-07-27T12:05:00+00:00', reason='XML changed',
        changed_paths=(xml,),
    )
    journal.append(
        'session_resettle_started', source_manifest_id='old-session',
        replacement_manifest_id='replacement-session', room_id=123,
        state='settling', session_paths=(video, xml), snapshot=snapshot,
        quiet_since='2026-07-27T12:10:00+00:00',
        started_at='2026-07-27T08:00:00+00:00',
    )
    journal.append(
        'session_manifest_ready', manifest_id='replacement-session',
        room_id=123, started_at='2026-07-27T08:00:00+00:00',
        settled_at='2026-07-27T12:40:00+00:00', flv_paths=(video,),
        snapshot=snapshot,
    )

    journal.append(
        'file_ready', fingerprint='fp1', manifest_id='replacement-session',
        file=video, xml_file=xml, start_time='2026-07-27T08:00:00+00:00',
        duration=3600,
    )

    state = journal.replay().files['fp1']
    assert state.manifest_id == 'replacement-session'
    assert state.event == 'upload_started'
    assert state.upload_started_at == '2026-07-27T12:01:00+00:00'
    assert state.description_fingerprint == 'description'
    assert state.attempt == 2
    assert state.video_id is None


def test_manifest_migration_preserves_retry_lifecycle_fields(tmp_path):
    state = _append_single_file_replacement(
        JsonlJournal(tmp_path / 'state.jsonl'),
        publication_events=(
            ('upload_started', {
                'file': '/recording/video.flv',
                'xml_file': '/recording/video.xml',
                'title': 'title', 'duration': 3600,
                'description_fingerprint': 'description',
                'upload_started_at': '2026-07-27T12:01:00+00:00',
                'attempt': 1,
            }),
            ('stage_retry_scheduled', {
                'stage': 'video', 'status': 'retryable',
                'retry_at': '2026-07-27T13:00:00+00:00', 'attempt': 2,
                'error_message': 'network unavailable',
            }),
        ),
    )

    assert state.event == 'stage_retry_scheduled'
    assert state.upload_started_at == '2026-07-27T12:01:00+00:00'
    assert state.retry_at == '2026-07-27T13:00:00+00:00'
    assert state.attempt == 2
    assert state.stage == 'video'
    assert state.status == 'retryable'
    assert state.error_message == 'network unavailable'


def test_attempted_publication_cannot_be_reclassified_as_ignored(tmp_path):
    with pytest.raises(ValueError, match='ready classification'):
        _append_single_file_replacement(
            JsonlJournal(tmp_path / 'state.jsonl'),
            replacement_event='ignored_tiny',
            publication_events=((
                'video_uploaded', {'video_id': 'yt123'},
            ),),
        )


@pytest.mark.parametrize(
    'classification_event',
    ['baseline', 'file_ready', 'ignored_invalid', 'ignored_tiny',
     'ignored_invalid_tail'],
)
def test_same_generation_publication_cannot_be_reclassified(
    tmp_path, classification_event
):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append(
        'file_ready', fingerprint='fp1', manifest_id='session-1',
        file='/recording/video.flv', xml_file='/recording/video.xml',
    )
    journal.append(
        'upload_started', fingerprint='fp1', title='title', duration=60,
        upload_started_at='2026-07-27T12:01:00+00:00', attempt=1,
    )
    before = journal.path.read_bytes()
    fields = {
        'fingerprint': 'fp1', 'manifest_id': 'session-1',
        'file': '/recording/video.flv',
        'xml_file': '/recording/video.xml',
    }
    if classification_event.startswith('ignored_'):
        fields['reason'] = 'new classification'

    with pytest.raises(ValueError, match='same generation'):
        journal.append(classification_event, **fields)

    assert journal.path.read_bytes() == before
    assert journal.replay().files['fp1'].event == 'upload_started'


@pytest.mark.parametrize(
    ('initial_event', 'replacement_event'),
    [
        ('ignored_tiny', 'file_ready'),
        ('ignored_invalid', 'ignored_tiny'),
        ('ignored_invalid_tail', 'ignored_invalid'),
    ],
)
def test_unpublished_ignored_state_can_be_reclassified_in_replacement(
    tmp_path, initial_event, replacement_event,
):
    state = _append_single_file_replacement(
        JsonlJournal(tmp_path / 'state.jsonl'),
        initial_event=initial_event,
        replacement_event=replacement_event,
    )

    assert state.manifest_id == 'replacement-session'
    assert state.event == replacement_event
    if replacement_event.startswith('ignored_'):
        assert state.reason == 'replacement classification'


@pytest.mark.parametrize(
    ('initial_event', 'publication_events'),
    [
        ('file_ready', ()),
        ('ignored_tiny', ()),
        ('file_ready', (('video_uploaded', {'video_id': 'yt123'}),)),
        ('file_ready', (('upload_started', {
            'file': '/recording/video.flv',
            'xml_file': '/recording/video.xml',
            'title': 'title', 'duration': 3600,
            'description_fingerprint': 'description',
            'upload_started_at': '2026-07-27T12:01:00+00:00',
            'attempt': 1,
        }),)),
    ],
)
def test_xml_migration_without_durable_remote_caption_uses_normal_caption_path(
    tmp_path, initial_event, publication_events,
):
    state = _append_single_file_replacement(
        JsonlJournal(tmp_path / 'state.jsonl'),
        initial_event=initial_event,
        replacement_event='file_ready',
        old_xml=(10, 1),
        new_xml=(20, 2),
        publication_events=publication_events,
    )

    assert state.caption_uploaded is False
    assert state.caption_refresh_required is False
    assert state.caption_status == 'pending'


def test_manifest_migration_follows_multiple_exact_replacement_links(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    video = '/recording/video.flv'
    xml = '/recording/video.xml'
    snapshots = (
        {video: (100, 1), xml: (10, 1)},
        {video: (100, 1), xml: (20, 2)},
        {video: (100, 1), xml: (30, 3)},
    )
    started_at = '2026-07-27T08:00:00+00:00'
    journal.append('initialized')
    journal.append(
        'session_state', room_id=123, state='waiting', session_id=None,
        session_paths=(), snapshot=snapshots[0], quiet_since=None,
        started_at=None,
    )
    journal.append(
        'session_manifest_ready', manifest_id='manifest-1', room_id=123,
        started_at=started_at, settled_at='2026-07-27T12:00:00+00:00',
        flv_paths=(video,), snapshot=snapshots[0],
    )
    journal.append(
        'file_ready', fingerprint='fp1', manifest_id='manifest-1',
        file=video, xml_file=xml,
    )
    journal.append('video_uploaded', fingerprint='fp1', video_id='yt123')
    journal.append(
        'caption_uploaded', fingerprint='fp1', caption_track_id='track-1'
    )

    for index in (0, 1):
        source = f'manifest-{index + 1}'
        target = f'manifest-{index + 2}'
        detected_minute = 5 + index * 45
        quiet_minute = 10 + index * 45
        settled_minute = 40 + index * 45
        journal.append(
            'session_manifest_changed', manifest_id=source,
            detected_at=(
                f'2026-07-27T12:{detected_minute:02d}:00+00:00'
                if detected_minute < 60 else '2026-07-27T13:05:00+00:00'
            ),
            reason='XML changed', changed_paths=(xml,),
        )
        journal.append(
            'session_state', room_id=123, state='waiting', session_id=None,
            session_paths=(), snapshot=snapshots[index + 1],
            quiet_since=None, started_at=None,
        )
        journal.append(
            'session_resettle_started', source_manifest_id=source,
            replacement_manifest_id=target, room_id=123, state='settling',
            session_paths=(video, xml), snapshot=snapshots[index + 1],
            quiet_since=(
                f'2026-07-27T12:{quiet_minute:02d}:00+00:00'
                if quiet_minute < 60 else '2026-07-27T13:10:00+00:00'
            ),
            started_at=started_at,
        )
        journal.append(
            'session_manifest_ready', manifest_id=target, room_id=123,
            started_at=started_at,
            settled_at=(
                f'2026-07-27T12:{settled_minute:02d}:00+00:00'
                if settled_minute < 60 else '2026-07-27T13:25:00+00:00'
            ),
            flv_paths=(video,), snapshot=snapshots[index + 1],
        )

    journal.append(
        'file_ready', fingerprint='fp1', manifest_id='manifest-3',
        file=video, xml_file=xml,
    )

    state = journal.replay().files['fp1']
    assert state.manifest_id == 'manifest-3'
    assert state.video_id == 'yt123'
    assert state.caption_uploaded is False
    assert state.caption_refresh_required is True
    assert state.caption_track_id == 'track-1'


def test_consecutive_xml_migrations_preserve_pending_caption_refresh(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    state = _append_single_file_replacement(
        journal,
        old_xml=(10, 1),
        new_xml=(20, 2),
        publication_events=(
            ('video_uploaded', {'video_id': 'yt123'}),
            ('caption_uploaded', {}),
        ),
    )
    assert state.caption_uploaded is False
    assert state.caption_refresh_required is True
    assert state.caption_track_id is None

    video = '/recording/video.flv'
    xml = '/recording/video.xml'
    final_snapshot = {video: (100, 1), xml: (30, 3)}
    journal.append(
        'session_manifest_changed', manifest_id='replacement-session',
        detected_at='2026-07-27T12:45:00+00:00',
        reason='XML changed again', changed_paths=(xml,),
    )
    journal.append(
        'session_state', room_id=123, state='waiting', session_id=None,
        session_paths=(), snapshot=final_snapshot, quiet_since=None,
        started_at=None,
    )
    journal.append(
        'session_resettle_started',
        source_manifest_id='replacement-session',
        replacement_manifest_id='final-session', room_id=123,
        state='settling', session_paths=(video, xml),
        snapshot=final_snapshot,
        quiet_since='2026-07-27T12:50:00+00:00',
        started_at='2026-07-27T08:00:00+00:00',
    )
    journal.append(
        'session_manifest_ready', manifest_id='final-session', room_id=123,
        started_at='2026-07-27T08:00:00+00:00',
        settled_at='2026-07-27T13:20:00+00:00', flv_paths=(video,),
        snapshot=final_snapshot,
    )
    journal.append(
        'file_ready', fingerprint='fp1', manifest_id='final-session',
        file=video, xml_file=xml, caption_status='pending',
    )

    replayed = JsonlJournal(journal.path).replay().files['fp1']
    assert replayed.manifest_id == 'final-session'
    assert replayed.caption_uploaded is False
    assert replayed.caption_refresh_required is True
    assert replayed.caption_track_id is None
    assert replayed.caption_status == 'pending'


@pytest.mark.parametrize(
    ('damage', 'message'),
    [
        ('cycle', 'cycle'),
        ('missing', 'missing link'),
        ('cross-room', 'cross rooms'),
    ],
)
def test_manifest_migration_rejects_damaged_replacement_chains(
    damage, message,
):
    video = '/recording/video.flv'
    snapshot = {video: (100, 1)}

    def manifest(
        manifest_id, *, invalidated=False, replacement=None, room_id=123,
    ):
        return JournalManifest(
            manifest_id=manifest_id, room_id=room_id,
            started_at='2026-07-27T08:00:00+00:00',
            settled_at='2026-07-27T12:00:00+00:00',
            flv_paths=(video,), snapshot=snapshot, invalidated=invalidated,
            invalidated_at=(
                '2026-07-27T11:55:00+00:00' if invalidated else None
            ),
            replacement_manifest_id=replacement,
        )

    if damage == 'cycle':
        manifests = (
            manifest('old', invalidated=True, replacement='middle'),
            manifest('middle', invalidated=True, replacement='old'),
            manifest('final'),
        )
    elif damage == 'missing':
        manifests = (
            manifest('old', invalidated=True, replacement='missing'),
            manifest('final'),
        )
    else:
        manifests = (
            manifest('old', invalidated=True, replacement='final'),
            manifest('final', room_id=456),
        )
    replay = type('Replay', (), {'manifests': manifests})()
    existing = JournalFileState(
        fingerprint='fp1', event='file_ready', manifest_id='old', file=video
    )
    classified = JournalFileState(
        fingerprint='fp1', event='file_ready', manifest_id='final', file=video
    )

    with pytest.raises(ValueError, match=message):
        journal_module._controlled_manifest_migration(
            replay, existing, classified, 'file_ready'
        )


def test_manifest_and_resettle_collections_are_defensively_frozen():
    flv_paths = ['/video.flv']
    changed_paths = ['/video.flv']
    manifest = JournalManifest(
        manifest_id='session-1',
        room_id=123,
        started_at='2026-07-27T08:00:00+00:00',
        settled_at='2026-07-27T12:00:00+00:00',
        flv_paths=flv_paths,
        snapshot={'/video.flv': (100, 200)},
        changed_paths=changed_paths,
    )
    request = JournalResettleRequest(
        source_manifest_id='session-1',
        settled_at=manifest.settled_at,
        detected_at='2026-07-27T12:05:00+00:00',
        reason='changed',
        changed_paths=changed_paths,
    )
    pending = [request]
    replay = JournalReplay(
        files={},
        manifests=[manifest],
        session=JournalSessionState(
            state=SessionState.WAITING,
            room_id=123,
            session_id=None,
            session_paths=(),
            snapshot={},
            quiet_since=None,
            started_at=None,
        ),
        initialized=True,
        pending_resettles=pending,
    )

    flv_paths.append('/late.flv')
    changed_paths.append('/late.flv')
    pending.clear()

    assert manifest.flv_paths == ('/video.flv',)
    assert manifest.changed_paths == ('/video.flv',)
    assert request.changed_paths == ('/video.flv',)
    assert replay.manifests == (manifest,)
    assert replay.pending_resettles == (request,)


def test_upload_attempt_and_resolution_events_replace_only_attempt_state(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append(
        'file_ready',
        fingerprint='fp1',
        manifest_id='session-1',
        file='/video.flv',
        xml_file='/video.xml',
        start_time='2026-07-27T10:00:00+00:00',
    )
    journal.append(
        'upload_started',
        fingerprint='fp1',
        title='First title',
        duration=3600.5,
        upload_started_at='2026-07-27T11:00:00+00:00',
    )
    journal.append('video_upload_rejected', fingerprint='fp1')
    journal.append(
        'stage_retry_scheduled',
        fingerprint='fp1',
        stage='video',
        status='retryable',
        retry_at='2026-07-27T12:00:00+00:00',
        attempt=2,
    )
    journal.append(
        'fatal',
        fingerprint='fp1',
        stage='video',
        message='stale failure',
    )
    journal.append(
        'upload_started',
        fingerprint='fp1',
        title='Second title',
        duration=3601,
        upload_started_at='2026-07-27T12:01:00+00:00',
    )

    started = journal.replay().files['fp1']
    assert started.event == 'upload_started'
    assert started.file == '/video.flv'
    assert started.xml_file == '/video.xml'
    assert started.title == 'Second title'
    assert started.duration == 3601
    assert started.upload_started_at == '2026-07-27T12:01:00+00:00'
    assert started.attempt == 0
    assert started.stage is None
    assert started.status is None
    assert started.error_stage is None
    assert started.error_message is None
    assert started.retry_at is None
    assert started.video_upload_rejected is False
    assert started.video_id is None
    assert started.ambiguous is False

    journal.append('ambiguous', fingerprint='fp1')
    assert journal.replay().files['fp1'].ambiguous is True
    journal.append('video_uploaded', fingerprint='fp1', video_id='yt123')
    uploaded = journal.replay().files['fp1']
    assert uploaded.video_id == 'yt123'
    assert uploaded.video_upload_rejected is False
    assert uploaded.ambiguous is False


def test_later_publication_events_retain_completed_fields(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('file_ready', fingerprint='fp1', file='/video.flv')
    journal.append('video_uploaded', fingerprint='fp1', video_id='yt123')
    journal.append(
        'description_updated',
        fingerprint='fp1',
        description_fingerprint='description-hash',
    )
    journal.append(
        'caption_status', fingerprint='fp1', caption_status='ready'
    )
    journal.append('caption_uploaded', fingerprint='fp1')
    journal.append('playlist_inserted', fingerprint='fp1')
    journal.append('youtube_processed', fingerprint='fp1')
    journal.append(
        'stage_retry_scheduled',
        fingerprint='fp1',
        stage='processing',
        status='pending',
        retry_at='2026-07-27T13:00:00+00:00',
        attempt=3,
    )

    state = journal.replay().files['fp1']
    assert state.event == 'stage_retry_scheduled'
    assert state.video_id == 'yt123'
    assert state.description_fingerprint == 'description-hash'
    assert state.caption_status == 'ready'
    assert state.caption_uploaded is True
    assert state.playlist_inserted is True
    assert state.youtube_processed is True
    assert state.retry_at == '2026-07-27T13:00:00+00:00'
    assert state.attempt == 3
    assert state.stage == 'processing'
    assert state.status == 'pending'


@pytest.mark.parametrize(
    'record',
    [
        {'event': 'unknown', 'fingerprint': 'fp1'},
        {'event': 'baseline', 'fingerprint': 'fp1'},
        {'event': 'file_ready', 'file': '/video.flv'},
        {'event': 'upload_started', 'fingerprint': 'fp1', 'title': 'title'},
        {'event': 'video_uploaded', 'fingerprint': 'fp1'},
        {
            'event': 'stage_retry_scheduled',
            'fingerprint': 'fp1',
            'retry_at': 'later',
        },
    ],
)
def test_event_schema_failures_are_corruption(tmp_path, record):
    path = tmp_path / 'state.jsonl'
    path.write_text(
        json.dumps(record, separators=(',', ':')) + '\n', encoding='utf8'
    )

    with pytest.raises(JournalCorruptError, match='line 1'):
        JsonlJournal(path).replay()


def test_session_state_and_initialized_events_restore_json_tuple_shapes(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('initialized')
    journal.append(
        'session_state',
        room_id=123,
        state=SessionState.SETTLING,
        session_id='session-1',
        session_paths=('/a.flv', '/b.flv'),
        snapshot={
            '/a.flv': (100, 123456789),
            '/b.flv': (200, 123456790),
        },
        quiet_since='2026-07-27T12:00:00+00:00',
        started_at='2026-07-27T08:00:00+00:00',
    )

    replay = journal.replay()

    assert replay.initialized is True
    assert replay.session.state is SessionState.SETTLING
    assert replay.session.room_id == 123
    assert replay.session.session_id == 'session-1'
    assert replay.session.session_paths == ('/a.flv', '/b.flv')
    assert replay.session.snapshot == {
        '/a.flv': (100, 123456789),
        '/b.flv': (200, 123456790),
    }
    assert replay.session.quiet_since == '2026-07-27T12:00:00+00:00'
    assert replay.session.started_at == '2026-07-27T08:00:00+00:00'


def test_replayed_session_snapshot_can_be_reappended(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append(
        'session_state',
        room_id=123,
        state=SessionState.SETTLING,
        session_id='session-1',
        session_paths=('/video.flv',),
        snapshot={'/video.flv': (100, 123456789)},
        quiet_since='2026-07-27T12:00:00+00:00',
        started_at='2026-07-27T08:00:00+00:00',
    )
    replayed = journal.replay().session

    journal.append(
        'session_state',
        room_id=replayed.room_id,
        state=replayed.state,
        session_id=replayed.session_id,
        session_paths=replayed.session_paths,
        snapshot=replayed.snapshot,
        quiet_since=replayed.quiet_since,
        started_at=replayed.started_at,
    )

    assert journal.replay().session == replayed


def _waiting_session_fields(room_id):
    return {
        'room_id': room_id,
        'state': SessionState.WAITING,
        'session_id': None,
        'session_paths': (),
        'snapshot': {},
        'quiet_since': None,
        'started_at': None,
    }


def _ready_manifest_fields(room_id, name='video'):
    path = f'/recording/{name}.flv'
    return {
        'manifest_id': f'session-{name}',
        'room_id': room_id,
        'started_at': '2026-07-27T08:00:00+00:00',
        'settled_at': '2026-07-27T12:00:00+00:00',
        'flv_paths': (path,),
        'snapshot': {path: (100, 200)},
    }


def test_first_session_state_durably_binds_room_id(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')

    journal.append('session_state', **_waiting_session_fields(123))

    assert journal.replay().session.room_id == 123


def test_session_state_rejects_bound_room_id_change(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('session_state', **_waiting_session_fields(123))
    before = journal.path.read_bytes()

    with pytest.raises(ValueError, match='room_id'):
        journal.append('session_state', **_waiting_session_fields(456))

    assert journal.path.read_bytes() == before


def test_manifest_rejects_bound_session_room_mismatch(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('session_state', **_waiting_session_fields(123))

    with pytest.raises(ValueError, match='room_id'):
        journal.append(
            'session_manifest_ready', **_ready_manifest_fields(456)
        )


def test_session_state_rejects_prior_manifest_room_mismatch(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append(
        'session_manifest_ready', **_ready_manifest_fields(123)
    )

    with pytest.raises(ValueError, match='room_id'):
        journal.append('session_state', **_waiting_session_fields(456))


def test_retained_manifests_cannot_span_multiple_rooms(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append(
        'session_manifest_ready', **_ready_manifest_fields(123, 'first')
    )

    with pytest.raises(ValueError, match='room_id'):
        journal.append(
            'session_manifest_ready', **_ready_manifest_fields(456, 'second')
        )


def test_session_state_without_room_id_fails_closed(tmp_path):
    fields = _waiting_session_fields(123)
    del fields['room_id']

    with pytest.raises(TypeError, match='room_id'):
        JsonlJournal(tmp_path / 'state.jsonl').append(
            'session_state', **fields
        )


def test_partial_baseline_restart_remains_uninitialized_until_explicit_marker(
    tmp_path,
):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('baseline', fingerprint='baseline:1', file='/video.flv')

    restarted = JsonlJournal(journal.path).replay()
    assert restarted.initialized is False
    assert set(restarted.files) == {'baseline:1'}

    journal.append('initialized')
    assert JsonlJournal(journal.path).replay().initialized is True


def test_manifests_are_replaced_retained_and_ordered_deterministically(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append(
        'session_manifest_ready',
        manifest_id='later',
        room_id=123,
        started_at='2026-07-27T11:00:00+00:00',
        settled_at='2026-07-27T14:00:00+00:00',
        flv_paths=('/later.flv',),
        snapshot={'/later.flv': (400, 4)},
    )
    journal.append(
        'session_manifest_ready',
        manifest_id='first',
        room_id=123,
        started_at='2026-07-27T08:00:00+00:00',
        settled_at='2026-07-27T12:00:00+00:00',
        flv_paths=['/first.flv'],
        snapshot={'/first.flv': (100, 1)},
    )
    journal.append(
        'session_manifest_ready',
        manifest_id='second',
        room_id=123,
        started_at='2026-07-27T09:00:00+00:00',
        settled_at='2026-07-27T12:00:00+00:00',
        flv_paths=['/second.flv'],
        snapshot={'/second.flv': (200, 2)},
    )
    journal.append(
        'session_manifest_ready',
        manifest_id='later',
        room_id=123,
        started_at='2026-07-27T11:00:00+00:00',
        settled_at='2026-07-27T14:00:00+00:00',
        flv_paths=['/later.flv'],
        snapshot={'/later.flv': [400, 4]},
    )
    journal.append('session_manifest_completed', manifest_id='first')

    manifests = journal.replay().manifests

    assert [manifest.manifest_id for manifest in manifests] == [
        'first', 'second', 'later'
    ]
    assert manifests[0].completed is True
    assert manifests[1].completed is False
    assert manifests[2].flv_paths == ('/later.flv',)


def test_manifest_completion_without_ready_event_is_corruption(tmp_path):
    path = tmp_path / 'state.jsonl'
    path.write_text(
        '{"event":"session_manifest_completed","manifest_id":"missing"}\n',
        encoding='utf8',
    )

    with pytest.raises(JournalCorruptError, match='line 1'):
        JsonlJournal(path).replay()


@pytest.mark.parametrize(
    'field, value',
    [
        ('state', 'not-a-state'),
        ('session_paths', ['/okay.flv', 2]),
        ('snapshot', {'/video.flv': [100]}),
        ('snapshot', {'/video.flv': [True, 2]}),
        ('quiet_since', 123),
    ],
)
def test_invalid_session_state_fields_are_corruption(tmp_path, field, value):
    record = {
        'event': 'session_state',
        'room_id': 123,
        'state': 'waiting',
        'session_id': None,
        'session_paths': [],
        'snapshot': {},
        'quiet_since': None,
        'started_at': None,
    }
    record[field] = value
    path = tmp_path / 'state.jsonl'
    path.write_text(json.dumps(record) + '\n', encoding='utf8')

    with pytest.raises(JournalCorruptError, match='line 1'):
        JsonlJournal(path).replay()


def test_baseline_fingerprint_uses_resolved_path_and_metadata_without_reading(
    tmp_path, monkeypatch
):
    path = tmp_path / 'subdirectory' / '..' / 'video.flv'
    monkeypatch.setattr(
        type(path),
        'read_bytes',
        lambda self: pytest.fail('baseline fingerprint read file contents'),
    )

    first = baseline_fingerprint(path, size=100, mtime_ns=123456789)
    equivalent = baseline_fingerprint(
        path.resolve(), size=100, mtime_ns=123456789
    )
    changed = baseline_fingerprint(path, size=101, mtime_ns=123456789)

    assert first.startswith('baseline:')
    assert first == equivalent
    assert first != changed


def test_append_mutex_covers_serialization_through_fsync(tmp_path, monkeypatch):
    journal = JsonlJournal(tmp_path / 'state.jsonl')

    class TrackingLock:
        def __init__(self):
            self.lock = threading.Lock()
            self.held = False

        def __enter__(self):
            self.lock.acquire()
            self.held = True

        def __exit__(self, exception_type, exception, traceback):
            self.held = False
            self.lock.release()

    tracking_lock = TrackingLock()
    journal._mutex = tracking_lock
    original_dumps = journal_module.json.dumps
    monkeypatch.setattr(
        journal_module.json,
        'dumps',
        lambda *args, **kwargs: (
            pytest.fail('serialized outside journal mutex')
            if not tracking_lock.held
            else original_dumps(*args, **kwargs)
        ),
    )
    monkeypatch.setattr(
        journal_module.os,
        'fsync',
        lambda file_descriptor: (
            None
            if tracking_lock.held
            else pytest.fail('fsync called outside journal mutex')
        ),
    )

    journal.append('baseline', fingerprint='baseline:1', file='/video.flv')


def test_two_threads_append_complete_replayable_lines(tmp_path):
    path = tmp_path / 'state.jsonl'
    journal = JsonlJournal(path)
    count_per_thread = 40

    def append_batch(prefix):
        for index in range(count_per_thread):
            fingerprint = f'baseline:{prefix}:{index}'
            journal.append(
                'baseline', fingerprint=fingerprint, file=f'/{prefix}-{index}.flv'
            )

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(append_batch, prefix) for prefix in ('a', 'b')]
        for future in futures:
            future.result()

    lines = path.read_bytes().splitlines()
    assert len(lines) == count_per_thread * 2
    assert all(isinstance(json.loads(line), dict) for line in lines)
    assert len(journal.replay().files) == count_per_thread * 2


def test_process_lock_is_exclusive_releasable_and_keeps_lock_file(tmp_path):
    state_dir = tmp_path / 'nested' / 'state'
    first = ProcessLock(state_dir)
    lock_path = state_dir / 'monitor.lock'
    assert lock_path.is_file()

    with pytest.raises(AlreadyRunningError):
        ProcessLock(state_dir)

    first.close()
    first.close()
    assert lock_path.is_file()

    with ProcessLock(state_dir):
        with pytest.raises(AlreadyRunningError):
            ProcessLock(state_dir)

    assert lock_path.is_file()
    final = ProcessLock(state_dir)
    final.close()


def test_append_rejects_unknown_event_without_creating_journal(tmp_path):
    path = tmp_path / 'state.jsonl'

    with pytest.raises(ValueError, match='unknown event'):
        JsonlJournal(path).append('future_guess', fingerprint='fp1')

    assert not path.exists()


@pytest.mark.parametrize(
    'event',
    ['ignored_invalid', 'ignored_tiny', 'ignored_invalid_tail'],
)
def test_known_ignored_file_events_create_replayable_state(tmp_path, event):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append(
        event,
        fingerprint=f'fp-{event}',
        file=f'/{event}.flv',
        reason='measured classification reason',
        measured_size=123456,
    )

    state = journal.replay().files[f'fp-{event}']
    assert state.event == event
    assert state.reason == 'measured classification reason'
    assert state.error_message == 'measured classification reason'
    assert json.loads(journal.path.read_text(encoding='utf8'))[
        'measured_size'
    ] == 123456


@pytest.mark.parametrize('reason', [None, '', 123])
def test_ignored_event_invalid_reason_is_rejected_before_append(tmp_path, reason):
    path = tmp_path / 'state.jsonl'
    fields = {
        'fingerprint': 'fp1',
        'file': '/video.flv',
    }
    if reason is not None:
        fields['reason'] = reason

    with pytest.raises(TypeError, match='reason'):
        JsonlJournal(path).append('ignored_invalid', **fields)

    assert not path.exists()


@pytest.mark.parametrize('reason', [None, '', 123])
def test_ignored_event_invalid_reason_is_corruption_on_replay(tmp_path, reason):
    record = {
        'event': 'ignored_tiny',
        'fingerprint': 'fp1',
        'file': '/video.flv',
    }
    if reason is not None:
        record['reason'] = reason
    path = tmp_path / 'state.jsonl'
    path.write_text(json.dumps(record) + '\n', encoding='utf8')

    with pytest.raises(JournalCorruptError, match='line 1'):
        JsonlJournal(path).replay()


@pytest.mark.parametrize(
    'field, value',
    [
        ('manifest_id', 123),
        ('xml_file', 123),
        ('title', 123),
        ('start_time', 123),
        ('duration', 'one hour'),
        ('caption_status', 123),
        ('source_size', True),
        ('source_mtime_ns', -1),
    ],
)
def test_invalid_file_metadata_types_are_corruption(tmp_path, field, value):
    record = {
        'event': 'file_ready',
        'fingerprint': 'fp1',
        'file': '/video.flv',
        field: value,
    }
    path = tmp_path / 'state.jsonl'
    path.write_text(json.dumps(record) + '\n', encoding='utf8')

    with pytest.raises(JournalCorruptError, match='line 1'):
        JsonlJournal(path).replay()


def test_append_repairs_ignored_torn_tail_before_writing_next_event(tmp_path):
    path = tmp_path / 'state.jsonl'
    path.write_bytes(
        b'{"event":"baseline","fingerprint":"baseline:1","file":"/a.flv"}\n'
        b'{"event":"baseline"'
    )
    journal = JsonlJournal(path)
    assert set(journal.replay().files) == {'baseline:1'}

    journal.append('baseline', fingerprint='baseline:2', file='/b.flv')

    assert set(journal.replay().files) == {'baseline:1', 'baseline:2'}
    assert len(path.read_bytes().splitlines()) == 2


def test_append_separates_valid_unterminated_event_from_next_event(tmp_path):
    path = tmp_path / 'state.jsonl'
    path.write_bytes(
        b'{"event":"baseline","fingerprint":"baseline:1","file":"/a.flv"}'
    )

    JsonlJournal(path).append(
        'baseline', fingerprint='baseline:2', file='/b.flv'
    )

    assert set(JsonlJournal(path).replay().files) == {
        'baseline:1', 'baseline:2'
    }
    assert len(path.read_bytes().splitlines()) == 2


def test_append_rejects_history_invalid_stage_without_mutating_journal(tmp_path):
    path = tmp_path / 'state.jsonl'
    journal = JsonlJournal(path)

    with pytest.raises(ValueError, match='existing file state'):
        journal.append('video_uploaded', fingerprint='fp1', video_id='yt123')

    assert not path.exists()


def test_video_upload_rejected_cannot_discard_existing_video_id(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('file_ready', fingerprint='fp1', file='/video.flv')
    journal.append('video_uploaded', fingerprint='fp1', video_id='yt123')
    before = journal.path.read_bytes()

    with pytest.raises(ValueError, match='existing video_id'):
        journal.append('video_upload_rejected', fingerprint='fp1')

    assert journal.path.read_bytes() == before
    state = journal.replay().files['fp1']
    assert state.video_id == 'yt123'
    assert state.event == 'video_uploaded'


def test_repeated_video_uploaded_is_idempotent_only_for_same_id(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('file_ready', fingerprint='fp1', file='/video.flv')
    journal.append('video_uploaded', fingerprint='fp1', video_id='yt123')
    journal.append(
        'description_updated',
        fingerprint='fp1',
        description_fingerprint='description-hash',
    )
    expected = journal.replay().files['fp1']

    journal.append('video_uploaded', fingerprint='fp1', video_id='yt123')

    assert journal.replay().files['fp1'] == expected
    before_conflict = journal.path.read_bytes()
    with pytest.raises(ValueError, match='different video_id'):
        journal.append('video_uploaded', fingerprint='fp1', video_id='other')
    assert journal.path.read_bytes() == before_conflict
    assert journal.replay().files['fp1'].video_id == 'yt123'


def test_ambiguous_upload_requires_resolution_before_reupload(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('file_ready', fingerprint='fp1', file='/video.flv')
    journal.append('ambiguous', fingerprint='fp1')
    before = journal.path.read_bytes()
    retry = {
        'title': 'Retry title',
        'duration': 120,
        'upload_started_at': '2026-07-27T13:01:00+00:00',
    }

    with pytest.raises(ValueError, match='ambiguous'):
        journal.append('upload_started', fingerprint='fp1', **retry)

    assert journal.path.read_bytes() == before
    assert journal.replay().files['fp1'].ambiguous is True

    journal.append('video_upload_rejected', fingerprint='fp1')
    journal.append('upload_started', fingerprint='fp1', **retry)
    state = journal.replay().files['fp1']
    assert state.event == 'upload_started'
    assert state.video_id is None
    assert state.ambiguous is False


def test_append_rejects_manifest_completion_without_ready_event(tmp_path):
    path = tmp_path / 'state.jsonl'

    with pytest.raises(ValueError, match='existing ready manifest'):
        JsonlJournal(path).append(
            'session_manifest_completed', manifest_id='missing'
        )

    assert not path.exists()


def test_duplicate_ready_event_does_not_reopen_completed_manifest(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    ready = {
        'manifest_id': 'session-1',
        'room_id': 123,
        'started_at': '2026-07-27T08:00:00+00:00',
        'settled_at': '2026-07-27T12:00:00+00:00',
        'flv_paths': ('/video.flv',),
        'snapshot': {'/video.flv': (100, 200)},
    }
    journal.append('session_manifest_ready', **ready)
    journal.append('session_manifest_completed', manifest_id='session-1')
    journal.append('session_manifest_ready', **ready)

    assert journal.replay().manifests[0].completed is True


@pytest.mark.parametrize(
    'event, fields',
    [
        ('description_updated', {'description_fingerprint': 'hash'}),
        ('caption_uploaded', {}),
        ('playlist_inserted', {}),
        ('youtube_processed', {}),
    ],
)
def test_completed_remote_stage_requires_existing_video_id(
    tmp_path, event, fields
):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('file_ready', fingerprint='fp1', file='/video.flv')

    with pytest.raises(ValueError, match='existing video_id'):
        journal.append(event, fingerprint='fp1', **fields)


def test_source_deleted_requires_path_and_reason_but_retains_file_identity(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('baseline', fingerprint='baseline:1', file='/video.flv')
    journal.append(
        'source_deleted',
        fingerprint='baseline:1',
        path='/video.flv',
        reason='disk pressure',
    )

    state = journal.replay().files['baseline:1']
    assert state.event == 'baseline'
    assert state.file == '/video.flv'
    assert state.deleted_paths == ('/video.flv',)


def test_source_deleted_without_path_is_rejected_before_append(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('baseline', fingerprint='baseline:1', file='/video.flv')
    before = journal.path.read_bytes()

    with pytest.raises(TypeError, match='path'):
        journal.append(
            'source_deleted', fingerprint='baseline:1', reason='disk pressure'
        )

    assert journal.path.read_bytes() == before


def test_caption_source_identity_replays_with_bound_xml_path(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append(
        'file_ready', fingerprint='fp1', file='/video.flv',
        xml_file='/video.xml',
    )

    journal.append(
        'caption_source_frozen',
        fingerprint='fp1',
        xml_file='/video.xml',
        caption_source_xml_size=123,
        caption_source_xml_mtime_ns=456,
    )

    state = JsonlJournal(journal.path).replay().files['fp1']
    assert state.event == 'caption_source_frozen'
    assert state.xml_file == '/video.xml'
    assert state.caption_source_xml_size == 123
    assert state.caption_source_xml_mtime_ns == 456


@pytest.mark.parametrize(
    ('fields', 'message'),
    [
        ({'caption_source_xml_size': 1}, 'mtime'),
        ({'caption_source_xml_mtime_ns': 1}, 'size'),
        ({
            'caption_source_xml_size': -1,
            'caption_source_xml_mtime_ns': 1,
        }, 'non-negative'),
        ({
            'caption_source_xml_size': True,
            'caption_source_xml_mtime_ns': 1,
        }, 'non-negative'),
    ],
)
def test_caption_source_identity_rejects_missing_or_invalid_numbers(
    tmp_path, fields, message
):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append(
        'file_ready', fingerprint='fp1', file='/video.flv',
        xml_file='/video.xml',
    )
    before = journal.path.read_bytes()

    with pytest.raises((TypeError, ValueError), match=message):
        journal.append(
            'caption_source_frozen', fingerprint='fp1',
            xml_file='/video.xml', **fields,
        )

    assert journal.path.read_bytes() == before


def test_caption_source_identity_rejects_different_xml_binding(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append(
        'file_ready', fingerprint='fp1', file='/video.flv',
        xml_file='/video.xml',
    )
    before = journal.path.read_bytes()

    with pytest.raises(ValueError, match='XML path'):
        journal.append(
            'caption_source_frozen', fingerprint='fp1',
            xml_file='/other.xml', caption_source_xml_size=1,
            caption_source_xml_mtime_ns=2,
        )

    assert journal.path.read_bytes() == before


def test_exact_duplicate_caption_source_identity_is_idempotent(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append(
        'file_ready', fingerprint='fp1', file='/video.flv',
        xml_file='/video.xml',
    )
    fields = {
        'xml_file': '/video.xml',
        'caption_source_xml_size': 123,
        'caption_source_xml_mtime_ns': 456,
    }
    journal.append('caption_source_frozen', fingerprint='fp1', **fields)
    journal.append(
        'stage_retry_scheduled', fingerprint='fp1', stage='caption',
        status='retryable', retry_at='2026-07-27T13:00:00+00:00',
        attempt=1,
    )

    journal.append('caption_source_frozen', fingerprint='fp1', **fields)

    state = journal.replay().files['fp1']
    assert state.event == 'stage_retry_scheduled'
    assert state.caption_source_xml_size == 123
    assert state.caption_source_xml_mtime_ns == 456


@pytest.mark.parametrize(
    ('field', 'value'),
    [
        ('xml_file', '/other.xml'),
        ('caption_source_xml_size', 124),
        ('caption_source_xml_mtime_ns', 457),
    ],
)
def test_caption_source_identity_is_immutable_within_generation(
    tmp_path, field, value
):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append(
        'file_ready', fingerprint='fp1', file='/video.flv',
        xml_file='/video.xml',
    )
    fields = {
        'xml_file': '/video.xml',
        'caption_source_xml_size': 123,
        'caption_source_xml_mtime_ns': 456,
    }
    journal.append('caption_source_frozen', fingerprint='fp1', **fields)
    before = journal.path.read_bytes()
    fields[field] = value

    with pytest.raises(ValueError, match='immutable'):
        journal.append('caption_source_frozen', fingerprint='fp1', **fields)

    assert journal.path.read_bytes() == before


def test_manifest_migration_clears_caption_source_identity(tmp_path):
    state = _append_single_file_replacement(
        JsonlJournal(tmp_path / 'state.jsonl'),
        publication_events=((
            'caption_source_frozen', {
                'xml_file': '/recording/video.xml',
                'caption_source_xml_size': 10,
                'caption_source_xml_mtime_ns': 1,
            },
        ),),
    )

    assert state.manifest_id == 'replacement-session'
    assert state.caption_source_xml_size is None
    assert state.caption_source_xml_mtime_ns is None


@pytest.mark.parametrize(
    'missing_field', ['stage', 'status', 'retry_at', 'attempt']
)
def test_retry_event_missing_required_field_is_rejected_before_append(
    tmp_path, missing_field
):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('file_ready', fingerprint='fp1', file='/video.flv')
    fields = {
        'stage': 'caption',
        'status': 'retryable',
        'retry_at': '2026-07-27T13:00:00+00:00',
        'attempt': 2,
    }
    del fields[missing_field]
    before = journal.path.read_bytes()

    with pytest.raises((TypeError, ValueError), match=missing_field):
        journal.append(
            'stage_retry_scheduled', fingerprint='fp1', **fields
        )

    assert journal.path.read_bytes() == before


@pytest.mark.parametrize(
    'field, value',
    [
        ('stage', 1),
        ('status', False),
        ('retry_at', None),
        ('attempt', 1.5),
    ],
)
def test_retry_event_wrong_field_type_is_corruption(tmp_path, field, value):
    ready = {
        'event': 'file_ready',
        'fingerprint': 'fp1',
        'file': '/video.flv',
    }
    retry = {
        'event': 'stage_retry_scheduled',
        'fingerprint': 'fp1',
        'stage': 'caption',
        'status': 'retryable',
        'retry_at': '2026-07-27T13:00:00+00:00',
        'attempt': 2,
    }
    retry[field] = value
    path = tmp_path / 'state.jsonl'
    path.write_text(
        json.dumps(ready) + '\n' + json.dumps(retry) + '\n', encoding='utf8'
    )

    with pytest.raises(JournalCorruptError, match='line 2'):
        JsonlJournal(path).replay()


def test_upload_started_uses_explicit_attempt_and_clears_stale_outcome(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('file_ready', fingerprint='fp1', file='/video.flv')
    journal.append(
        'stage_retry_scheduled',
        fingerprint='fp1',
        stage='video',
        status='retryable',
        retry_at='2026-07-27T13:00:00+00:00',
        attempt=2,
    )

    journal.append(
        'upload_started',
        fingerprint='fp1',
        title='Retry title',
        duration=120,
        upload_started_at='2026-07-27T13:01:00+00:00',
        attempt=3,
    )

    state = journal.replay().files['fp1']
    assert state.attempt == 3
    assert state.stage is None
    assert state.status is None
    assert state.retry_at is None


def test_extra_diagnostic_fields_are_accepted_without_changing_state_schema(
    tmp_path,
):
    journal = JsonlJournal(tmp_path / 'state.jsonl')

    journal.append(
        'file_ready',
        fingerprint='fp1',
        file='/video.flv',
        measured_size=123456,
        diagnostics={'probe': 'clean', 'streams': 2},
    )

    record = json.loads(journal.path.read_text(encoding='utf8'))
    assert record['measured_size'] == 123456
    assert record['diagnostics'] == {'probe': 'clean', 'streams': 2}
    assert journal.replay().files['fp1'].event == 'file_ready'


def test_uncompleted_manifest_conflict_is_rejected(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    ready = {
        'manifest_id': 'session-1',
        'room_id': 123,
        'started_at': '2026-07-27T08:00:00+00:00',
        'settled_at': '2026-07-27T12:00:00+00:00',
        'flv_paths': ('/video.flv',),
        'snapshot': {'/video.flv': (100, 200)},
    }
    journal.append('session_manifest_ready', **ready)
    before = journal.path.read_bytes()

    with pytest.raises(ValueError, match='different data'):
        journal.append(
            'session_manifest_ready',
            **dict(
                ready,
                flv_paths=('/different.flv',),
                snapshot={'/different.flv': (100, 200)},
            ),
        )

    assert journal.path.read_bytes() == before


def test_manifest_rejects_duplicate_flv_paths(tmp_path):
    path = tmp_path / 'state.jsonl'

    with pytest.raises(ValueError, match='duplicate'):
        JsonlJournal(path).append(
            'session_manifest_ready',
            manifest_id='session-1',
            room_id=123,
            started_at='2026-07-27T08:00:00+00:00',
            settled_at='2026-07-27T12:00:00+00:00',
            flv_paths=('/video.flv', '/video.flv'),
        )

    assert not path.exists()


@pytest.mark.parametrize('lifecycle', ['baseline', 'ignored', 'processed'])
def test_source_deletions_preserve_lifecycle_and_accumulate_paths(
    tmp_path, lifecycle
):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    fingerprint = f'fp-{lifecycle}'
    common = {
        'fingerprint': fingerprint,
        'file': '/video.flv',
        'xml_file': '/video.xml',
    }
    if lifecycle == 'baseline':
        journal.append('baseline', **common)
        expected_event = 'baseline'
        expected_reason = None
    elif lifecycle == 'ignored':
        journal.append(
            'ignored_tiny', **common, reason='below non-tail size threshold'
        )
        expected_event = 'ignored_tiny'
        expected_reason = 'below non-tail size threshold'
    else:
        journal.append('file_ready', **common)
        journal.append('video_uploaded', fingerprint=fingerprint, video_id='yt1')
        journal.append('youtube_processed', fingerprint=fingerprint)
        expected_event = 'youtube_processed'
        expected_reason = None

    journal.append(
        'source_deleted',
        fingerprint=fingerprint,
        path='/video.flv',
        reason='disk pressure',
    )
    after_video = journal.replay().files[fingerprint]
    assert after_video.event == expected_event
    assert after_video.reason == expected_reason
    assert after_video.deleted_paths == ('/video.flv',)

    journal.append(
        'source_deleted',
        fingerprint=fingerprint,
        path='/video.xml',
        reason='disk pressure',
    )
    journal.append(
        'source_deleted',
        fingerprint=fingerprint,
        path='/video.flv',
        reason='idempotent cleanup replay',
    )
    after_xml = journal.replay().files[fingerprint]
    assert after_xml.event == expected_event
    assert after_xml.deleted_paths == ('/video.flv', '/video.xml')


def test_source_deleted_without_prior_state_fails_closed(tmp_path):
    path = tmp_path / 'state.jsonl'

    with pytest.raises(ValueError, match='existing file state'):
        JsonlJournal(path).append(
            'source_deleted',
            fingerprint='missing',
            path='/video.flv',
            reason='disk pressure',
        )

    assert not path.exists()


@pytest.mark.parametrize('terminal_event', ['fatal', 'ambiguous'])
def test_terminal_event_clears_retry_schedule_but_keeps_diagnostics(
    tmp_path, terminal_event
):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('file_ready', fingerprint='fp1', file='/video.flv')
    journal.append(
        'upload_started',
        fingerprint='fp1',
        title='Title',
        duration=120,
        upload_started_at='2026-07-27T11:00:00+00:00',
    )
    journal.append(
        'stage_retry_scheduled',
        fingerprint='fp1',
        stage='video',
        status='retryable',
        retry_at='2026-07-27T12:00:00+00:00',
        attempt=2,
    )

    journal.append(
        terminal_event,
        fingerprint='fp1',
        stage='video',
        message='manual review required',
    )

    state = journal.replay().files['fp1']
    assert state.event == terminal_event
    assert state.retry_at is None
    assert state.stage is None
    assert state.status is None
    assert state.attempt == 0
    assert state.error_stage == 'video'
    assert state.error_message == 'manual review required'
    assert state.ambiguous is (terminal_event == 'ambiguous')


def test_public_replay_mappings_are_copied_and_read_only():
    file_state = JournalFileState(fingerprint='fp1', event='baseline')
    files = {'fp1': file_state}
    snapshot = {'/video.flv': (100, 200)}
    session = JournalSessionState(
        state=SessionState.SETTLING,
        room_id=123,
        session_id='session-1',
        session_paths=('/video.flv',),
        snapshot=snapshot,
        quiet_since='2026-07-27T12:00:00+00:00',
        started_at='2026-07-27T08:00:00+00:00',
    )
    replay = JournalReplay(
        files=files,
        manifests=(),
        session=session,
        initialized=True,
    )

    files.clear()
    snapshot.clear()
    assert set(replay.files) == {'fp1'}
    assert replay.session.snapshot == {'/video.flv': (100, 200)}
    with pytest.raises(TypeError):
        replay.files['other'] = file_state
    with pytest.raises(TypeError):
        replay.session.snapshot['/other.flv'] = (1, 2)


@pytest.mark.parametrize(
    'event, fields',
    [
        (
            'upload_started',
            {
                'fingerprint': 'fp1',
                'title': 'Title',
                'duration': 120,
                'upload_started_at': '2026-07-27 11:00:00',
            },
        ),
        (
            'stage_retry_scheduled',
            {
                'fingerprint': 'fp1',
                'stage': 'video',
                'status': 'retryable',
                'retry_at': 'not-a-time',
                'attempt': 1,
            },
        ),
    ],
)
def test_file_safety_timestamps_require_timezone_aware_iso(
    tmp_path, event, fields
):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('file_ready', fingerprint='fp1', file='/video.flv')

    with pytest.raises((TypeError, ValueError), match='timezone-aware'):
        journal.append(event, **fields)


@pytest.mark.parametrize(
    'field, value',
    [('quiet_since', '2026-07-27T12:00:00'), ('started_at', 'invalid')],
)
def test_session_safety_timestamps_require_timezone_aware_iso(
    tmp_path, field, value
):
    fields = {
        'room_id': 123,
        'state': 'settling',
        'session_id': 'session-1',
        'session_paths': (),
        'snapshot': {},
        'quiet_since': '2026-07-27T12:00:00Z',
        'started_at': '2026-07-27T08:00:00+00:00',
    }
    fields[field] = value

    with pytest.raises((TypeError, ValueError), match='timezone-aware'):
        JsonlJournal(tmp_path / 'state.jsonl').append('session_state', **fields)


def test_manifests_sort_by_instant_across_offsets_and_accept_z(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append(
        'session_manifest_ready',
        manifest_id='later-instant',
        room_id=123,
        started_at='2026-07-27T03:00:00Z',
        settled_at='2026-07-27T04:00:00+00:00',
        flv_paths=('/later.flv',),
        snapshot={'/later.flv': (200, 2)},
    )
    journal.append(
        'session_manifest_ready',
        manifest_id='earlier-instant',
        room_id=123,
        started_at='2026-07-27T11:00:00+09:00',
        settled_at='2026-07-27T12:00:00+09:00',
        flv_paths=('/earlier.flv',),
        snapshot={'/earlier.flv': (100, 1)},
    )

    assert [item.manifest_id for item in journal.replay().manifests] == [
        'earlier-instant', 'later-instant'
    ]


def test_manifest_timestamps_reject_naive_values(tmp_path):
    with pytest.raises((TypeError, ValueError), match='timezone-aware'):
        JsonlJournal(tmp_path / 'state.jsonl').append(
            'session_manifest_ready',
            manifest_id='session-1',
            room_id=123,
            started_at='2026-07-27T08:00:00',
            settled_at='2026-07-27T12:00:00+00:00',
            flv_paths=('/video.flv',),
        )


def test_manifest_requires_frozen_identity_for_every_flv(tmp_path):
    with pytest.raises((TypeError, ValueError), match='snapshot'):
        JsonlJournal(tmp_path / 'state.jsonl').append(
            'session_manifest_ready',
            manifest_id='session-1',
            room_id=123,
            started_at='2026-07-27T08:00:00+00:00',
            settled_at='2026-07-27T12:00:00+00:00',
            flv_paths=('/video.flv',),
        )


def test_manifest_snapshot_replays_as_copied_read_only_mapping(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    snapshot = {
        '/video.flv': (100, 200),
        '/video.xml': (10, 20),
    }
    journal.append(
        'session_manifest_ready',
        manifest_id='session-1',
        room_id=123,
        started_at='2026-07-27T08:00:00+00:00',
        settled_at='2026-07-27T12:00:00+00:00',
        flv_paths=('/video.flv',),
        snapshot=snapshot,
    )
    snapshot.clear()

    frozen = journal.replay().manifests[0].snapshot

    assert frozen == {
        '/video.flv': (100, 200),
        '/video.xml': (10, 20),
    }
    with pytest.raises(TypeError):
        frozen['/other.flv'] = (1, 2)


def test_manifest_change_is_durable_idempotent_and_preserves_identity(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    original_snapshot = {
        '/recording/video.flv': (100, 200),
        '/recording/video.xml': (10, 20),
    }
    journal.append(
        'session_manifest_ready',
        manifest_id='session-1',
        room_id=123,
        started_at='2026-07-27T08:00:00+00:00',
        settled_at='2026-07-27T12:00:00+00:00',
        flv_paths=('/recording/video.flv',),
        snapshot=original_snapshot,
    )
    changed = {
        'manifest_id': 'session-1',
        'detected_at': '2026-07-27T12:05:00+00:00',
        'reason': 'frozen source identity changed',
        'changed_paths': ('/recording/video.flv',),
    }

    journal.append('session_manifest_changed', **changed)
    journal.append('session_manifest_changed', **changed)

    replay = journal.replay()
    manifest = replay.manifests[0]
    assert manifest.invalidated is True
    assert manifest.invalidated_at == changed['detected_at']
    assert manifest.invalidation_reason == changed['reason']
    assert manifest.changed_paths == changed['changed_paths']
    assert manifest.replacement_manifest_id is None
    assert manifest.flv_paths == ('/recording/video.flv',)
    assert dict(manifest.snapshot) == original_snapshot
    assert len(replay.pending_resettles) == 1
    request = replay.pending_resettles[0]
    assert request.source_manifest_id == 'session-1'
    assert request.settled_at == '2026-07-27T12:00:00+00:00'
    with pytest.raises(FrozenInstanceError):
        request.reason = 'changed'

    with pytest.raises(ValueError, match='conflicting invalidation'):
        journal.append(
            'session_manifest_changed',
            **dict(changed, reason='different reason'),
        )


def test_pending_resettles_sort_by_source_manifest_settlement(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    for manifest_id, settled_at, path in (
        ('later', '2026-07-27T13:00:00+00:00', '/later.flv'),
        ('earlier', '2026-07-27T12:00:00+00:00', '/earlier.flv'),
    ):
        journal.append(
            'session_manifest_ready',
            manifest_id=manifest_id,
            room_id=123,
            started_at='2026-07-27T08:00:00+00:00',
            settled_at=settled_at,
            flv_paths=(path,),
            snapshot={path: (100, 200)},
        )
        journal.append(
            'session_manifest_changed',
            manifest_id=manifest_id,
            detected_at='2026-07-27T14:00:00+00:00',
            reason='changed',
            changed_paths=(path,),
        )

    assert [
        item.source_manifest_id
        for item in journal.replay().pending_resettles
    ] == ['earlier', 'later']


def test_resettle_started_atomically_claims_request_and_session(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('initialized')
    journal.append(
        'session_state',
        room_id=123,
        state='waiting',
        session_id=None,
        session_paths=(),
        snapshot={'/recording/video.flv': (100, 200)},
        quiet_since=None,
        started_at=None,
    )
    journal.append(
        'session_manifest_ready',
        manifest_id='session-1',
        room_id=123,
        started_at='2026-07-27T08:00:00+00:00',
        settled_at='2026-07-27T12:00:00+00:00',
        flv_paths=('/recording/video.flv',),
        snapshot={'/recording/video.flv': (100, 200)},
    )
    journal.append(
        'session_manifest_changed',
        manifest_id='session-1',
        detected_at='2026-07-27T12:05:00+00:00',
        reason='changed',
        changed_paths=('/recording/video.flv',),
    )
    full_snapshot = {
        '/recording/video.flv': (101, 201),
        '/recording/video.xml': (11, 21),
        '/recording/unrelated.flv': (900, 900),
    }
    started = {
        'source_manifest_id': 'session-1',
        'replacement_manifest_id': 'replacement-1',
        'room_id': 123,
        'state': 'settling',
        'session_paths': (
            '/recording/video.flv', '/recording/video.xml'
        ),
        'snapshot': full_snapshot,
        'quiet_since': '2026-07-27T12:10:00+00:00',
        'started_at': '2026-07-27T08:00:00+00:00',
    }

    with pytest.raises(ValueError, match='quiet_since'):
        journal.append(
            'session_resettle_started',
            **dict(started, quiet_since='2026-07-27T07:59:00+00:00'),
        )

    journal.append('session_resettle_started', **started)

    replay = journal.replay()
    assert replay.pending_resettles == ()
    assert replay.manifests[0].replacement_manifest_id == 'replacement-1'
    assert replay.session.state is SessionState.SETTLING
    assert replay.session.session_id == 'replacement-1'
    assert replay.session.session_paths == started['session_paths']
    assert dict(replay.session.snapshot) == full_snapshot
    assert replay.session.quiet_since == started['quiet_since']
    assert replay.session.started_at == started['started_at']

    journal.append('session_resettle_started', **started)
    assert journal.replay() == replay

    with pytest.raises(ValueError, match='conflicting duplicate'):
        journal.append(
            'session_resettle_started',
            **dict(started, quiet_since='2026-07-27T12:11:00+00:00'),
        )

    with pytest.raises(ValueError, match='already claimed'):
        journal.append(
            'session_resettle_started',
            **dict(started, replacement_manifest_id='replacement-2'),
        )


def test_resettle_start_without_current_source_flv_fails_closed(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('initialized')
    journal.append(
        'session_state',
        room_id=123,
        state='waiting',
        session_id=None,
        session_paths=(),
        snapshot={},
        quiet_since=None,
        started_at=None,
    )
    journal.append(
        'session_manifest_ready',
        manifest_id='session-1',
        room_id=123,
        started_at='2026-07-27T08:00:00+00:00',
        settled_at='2026-07-27T12:00:00+00:00',
        flv_paths=('/recording/video.flv',),
        snapshot={'/recording/video.flv': (100, 200)},
    )
    journal.append(
        'session_manifest_changed',
        manifest_id='session-1',
        detected_at='2026-07-27T12:05:00+00:00',
        reason='source disappeared',
        changed_paths=('/recording/video.flv',),
    )

    with pytest.raises(ValueError, match='current source FLV'):
        journal.append(
            'session_resettle_started',
            source_manifest_id='session-1',
            replacement_manifest_id='replacement-1',
            room_id=123,
            state='settling',
            session_paths=('/recording/video.xml',),
            snapshot={'/recording/video.xml': (11, 21)},
            quiet_since='2026-07-27T12:10:00+00:00',
            started_at='2026-07-27T08:00:00+00:00',
        )

    replay = journal.replay()
    assert replay.session.state is SessionState.WAITING
    assert len(replay.pending_resettles) == 1


def test_duplicate_manifest_id_rejects_snapshot_conflict(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    ready = {
        'manifest_id': 'session-1',
        'room_id': 123,
        'started_at': '2026-07-27T08:00:00+00:00',
        'settled_at': '2026-07-27T12:00:00+00:00',
        'flv_paths': ('/video.flv',),
        'snapshot': {'/video.flv': (100, 200)},
    }
    journal.append('session_manifest_ready', **ready)

    with pytest.raises(ValueError, match='different data'):
        journal.append(
            'session_manifest_ready',
            **dict(ready, snapshot={'/video.flv': (101, 200)}),
        )


@pytest.mark.parametrize(
    'snapshot',
    [
        {'/video.flv': [100]},
        {'/video.flv': [True, 200]},
        {'/video.flv': [-1, 200]},
        {'/video.flv': '100,200'},
    ],
)
def test_manifest_rejects_malformed_snapshot_identity(tmp_path, snapshot):
    with pytest.raises((TypeError, ValueError), match='snapshot'):
        JsonlJournal(tmp_path / 'state.jsonl').append(
            'session_manifest_ready',
            manifest_id='session-1',
            room_id=123,
            started_at='2026-07-27T08:00:00+00:00',
            settled_at='2026-07-27T12:00:00+00:00',
            flv_paths=('/video.flv',),
            snapshot=snapshot,
        )


def test_manifest_rejects_duplicate_normalized_snapshot_paths(tmp_path):
    with pytest.raises(ValueError, match='duplicate normalized'):
        JsonlJournal(tmp_path / 'state.jsonl').append(
            'session_manifest_ready',
            manifest_id='session-1',
            room_id=123,
            started_at='2026-07-27T08:00:00+00:00',
            settled_at='2026-07-27T12:00:00+00:00',
            flv_paths=('/recording/video.flv',),
            snapshot={
                '/recording/video.flv': (100, 200),
                '/recording/parts/../video.flv': (100, 200),
            },
        )


def test_manifest_rejects_settlement_before_session_start(tmp_path):
    with pytest.raises(ValueError, match='before started_at'):
        JsonlJournal(tmp_path / 'state.jsonl').append(
            'session_manifest_ready',
            manifest_id='session-1',
            room_id=123,
            started_at='2026-07-27T12:00:00+00:00',
            settled_at='2026-07-27T11:59:59+00:00',
            flv_paths=('/video.flv',),
            snapshot={'/video.flv': (100, 200)},
        )


def test_manifest_rejects_empty_flv_paths(tmp_path):
    with pytest.raises(ValueError, match='at least one'):
        JsonlJournal(tmp_path / 'state.jsonl').append(
            'session_manifest_ready',
            manifest_id='session-1',
            room_id=123,
            started_at='2026-07-27T08:00:00+00:00',
            settled_at='2026-07-27T12:00:00+00:00',
            flv_paths=(),
            snapshot={'/video.xml': (10, 20)},
        )


@pytest.mark.parametrize(
    ('flv_path', 'snapshot'),
    [
        ('relative/video.flv', {'relative/video.flv': (100, 200)}),
        (
            '/recording/parts/../video.flv',
            {'/recording/parts/../video.flv': (100, 200)},
        ),
        (
            '/recording/video.flv',
            {
                '/recording/parts/../video.xml': (10, 20),
                '/recording/video.flv': (100, 200),
            },
        ),
    ],
)
def test_manifest_requires_lexically_normalized_absolute_paths(
    tmp_path, flv_path, snapshot
):
    with pytest.raises(ValueError, match='normalized absolute'):
        JsonlJournal(tmp_path / 'state.jsonl').append(
            'session_manifest_ready',
            manifest_id='session-1',
            room_id=123,
            started_at='2026-07-27T08:00:00+00:00',
            settled_at='2026-07-27T12:00:00+00:00',
            flv_paths=(flv_path,),
            snapshot=snapshot,
        )


def test_manifest_rejects_non_flv_media_path(tmp_path):
    with pytest.raises(ValueError, match=r'\.flv'):
        JsonlJournal(tmp_path / 'state.jsonl').append(
            'session_manifest_ready',
            manifest_id='session-1',
            room_id=123,
            started_at='2026-07-27T08:00:00+00:00',
            settled_at='2026-07-27T12:00:00+00:00',
            flv_paths=('/recording/video.mp4',),
            snapshot={'/recording/video.mp4': (100, 200)},
        )


def test_manifest_accepts_case_insensitive_flv_suffix(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append(
        'session_manifest_ready',
        manifest_id='session-1',
        room_id=123,
        started_at='2026-07-27T08:00:00+00:00',
        settled_at='2026-07-27T12:00:00+00:00',
        flv_paths=('/recording/video.FLV',),
        snapshot={'/recording/video.FLV': (100, 200)},
    )

    assert journal.replay().manifests[0].flv_paths == (
        '/recording/video.FLV',
    )


def test_manifest_snapshot_rejects_unrelated_directory_history(tmp_path):
    with pytest.raises(ValueError, match='unrelated'):
        JsonlJournal(tmp_path / 'state.jsonl').append(
            'session_manifest_ready',
            manifest_id='session-1',
            room_id=123,
            started_at='2026-07-27T08:00:00+00:00',
            settled_at='2026-07-27T12:00:00+00:00',
            flv_paths=('/recording/video.flv',),
            snapshot={
                '/recording/video.flv': (100, 200),
                '/recording/video.xml': (10, 20),
                '/recording/historical.flv': (900, 900),
            },
        )


def test_manifest_replay_is_independent_of_current_working_directory(
    tmp_path, monkeypatch
):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    video = str(tmp_path / 'recording' / 'video.flv')
    journal.append(
        'session_manifest_ready',
        manifest_id='session-1',
        room_id=123,
        started_at='2026-07-27T08:00:00+00:00',
        settled_at='2026-07-27T12:00:00+00:00',
        flv_paths=(video,),
        snapshot={video: (100, 200)},
    )
    other_directory = tmp_path / 'other'
    other_directory.mkdir()
    monkeypatch.chdir(other_directory)

    manifest = journal.replay().manifests[0]

    assert manifest.flv_paths == (video,)
    assert manifest.snapshot == {video: (100, 200)}


@pytest.mark.parametrize('start_time', ['not-a-time', '2026-07-27T08:00:00'])
def test_file_ready_start_time_requires_timezone_aware_iso(
    tmp_path, start_time
):
    path = tmp_path / 'state.jsonl'

    with pytest.raises((TypeError, ValueError), match='timezone-aware'):
        JsonlJournal(path).append(
            'file_ready',
            fingerprint='fp1',
            file='/video.flv',
            start_time=start_time,
        )

    assert not path.exists()


@pytest.mark.parametrize('start_time', ['invalid', '2026-07-27T08:00:00'])
def test_file_ready_invalid_start_time_is_corruption_on_replay(
    tmp_path, start_time
):
    path = tmp_path / 'state.jsonl'
    path.write_text(
        json.dumps({
            'event': 'file_ready',
            'fingerprint': 'fp1',
            'file': '/video.flv',
            'start_time': start_time,
        }) + '\n',
        encoding='utf8',
    )

    with pytest.raises(JournalCorruptError, match='line 1'):
        JsonlJournal(path).replay()


def test_two_journal_instances_share_lock_and_append_without_loss(tmp_path):
    path = tmp_path / 'state.jsonl'
    first = JsonlJournal(path)
    second = JsonlJournal(path.parent / '.' / path.name)
    assert first._mutex is second._mutex

    def append_batch(journal, prefix):
        for index in range(25):
            journal.append(
                'baseline',
                fingerprint=f'baseline:{prefix}:{index}',
                file=f'/{prefix}-{index}.flv',
            )

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(append_batch, first, 'first'),
            executor.submit(append_batch, second, 'second'),
        ]
        for future in futures:
            future.result()

    assert len(first.replay().files) == 50
    assert len(path.read_bytes().splitlines()) == 50


def test_journal_path_is_canonicalized_at_construction(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    journal = JsonlJournal('nested/../state.jsonl')

    assert journal.path == (tmp_path / 'state.jsonl').resolve()


def test_process_lock_rejects_nested_or_closed_context(tmp_path):
    process_lock = ProcessLock(tmp_path / 'state')
    with process_lock:
        with pytest.raises(RuntimeError, match='already entered'):
            process_lock.__enter__()

    with pytest.raises(RuntimeError, match='closed'):
        process_lock.__enter__()


def test_process_lock_closes_file_when_initial_fsync_fails(tmp_path, monkeypatch):
    state_dir = tmp_path / 'state'
    state_dir.mkdir()
    opened_files = []
    original_open = type(state_dir).open

    def tracked_open(path, *args, **kwargs):
        opened_file = original_open(path, *args, **kwargs)
        opened_files.append(opened_file)
        return opened_file

    monkeypatch.setattr(type(state_dir), 'open', tracked_open)
    monkeypatch.setattr(
        journal_module.os,
        'fsync',
        lambda file_descriptor: (_ for _ in ()).throw(OSError(errno.EIO, 'fail')),
    )

    with pytest.raises(OSError, match='fail'):
        ProcessLock(state_dir)

    assert len(opened_files) == 1
    assert opened_files[0].closed is True

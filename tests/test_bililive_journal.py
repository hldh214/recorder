import json
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

import recorder.bililive.journal as journal_module
from recorder.bililive.journal import JournalCorruptError, JsonlJournal
from recorder.bililive.journal import (
    AlreadyRunningError,
    ProcessLock,
    baseline_fingerprint,
)
from recorder.bililive.models import RoomState, SessionState


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
        retry_at='2026-07-27T12:00:00+00:00',
        attempt=2,
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
    assert started.attempt == 2
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
    assert replay.session.session_id == 'session-1'
    assert replay.session.session_paths == ('/a.flv', '/b.flv')
    assert replay.session.snapshot == {
        '/a.flv': (100, 123456789),
        '/b.flv': (200, 123456790),
    }
    assert replay.session.quiet_since == '2026-07-27T12:00:00+00:00'
    assert replay.session.started_at == '2026-07-27T08:00:00+00:00'


def test_baseline_event_marks_journal_initialized(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('baseline', fingerprint='baseline:1', file='/video.flv')

    assert journal.replay().initialized is True


def test_manifests_are_replaced_retained_and_ordered_deterministically(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append(
        'session_manifest_ready',
        manifest_id='later',
        room_id=123,
        started_at='2026-07-27T11:00:00+00:00',
        settled_at='2026-07-27T14:00:00+00:00',
        flv_paths=('/later.flv',),
    )
    journal.append(
        'session_manifest_ready',
        manifest_id='first',
        room_id=123,
        started_at='2026-07-27T08:00:00+00:00',
        settled_at='2026-07-27T12:00:00+00:00',
        flv_paths=['/first.flv'],
    )
    journal.append(
        'session_manifest_ready',
        manifest_id='second',
        room_id=123,
        started_at='2026-07-27T09:00:00+00:00',
        settled_at='2026-07-27T12:00:00+00:00',
        flv_paths=['/second.flv'],
    )
    journal.append(
        'session_manifest_ready',
        manifest_id='later',
        room_id=123,
        started_at='2026-07-27T10:30:00+00:00',
        settled_at='2026-07-27T13:00:00+00:00',
        flv_paths=['/later-replaced.flv'],
    )
    journal.append('session_manifest_completed', manifest_id='first')

    manifests = journal.replay().manifests

    assert [manifest.manifest_id for manifest in manifests] == [
        'first', 'second', 'later'
    ]
    assert manifests[0].completed is True
    assert manifests[1].completed is False
    assert manifests[2].flv_paths == ('/later-replaced.flv',)


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
    )

    state = journal.replay().files[f'fp-{event}']
    assert state.event == event
    assert state.error_message == 'measured classification reason'


@pytest.mark.parametrize(
    'field, value',
    [
        ('manifest_id', 123),
        ('xml_file', 123),
        ('title', 123),
        ('start_time', 123),
        ('duration', 'one hour'),
        ('caption_status', 123),
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
    assert state.event == 'source_deleted'
    assert state.file == '/video.flv'


def test_source_deleted_without_path_is_rejected_before_append(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('baseline', fingerprint='baseline:1', file='/video.flv')
    before = journal.path.read_bytes()

    with pytest.raises(TypeError, match='path'):
        journal.append(
            'source_deleted', fingerprint='baseline:1', reason='disk pressure'
        )

    assert journal.path.read_bytes() == before

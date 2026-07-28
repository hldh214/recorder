from types import SimpleNamespace

import pytest

from recorder.bililive.journal import AlreadyRunningError, ProcessLock
from recorder.bililive.models import RoomState, SessionState
from recorder.bililive.monitor import MonitorDecision
from recorder.utils.bililive_directory_monitor import (
    _dry_run_media_report,
    run_monitor,
)


ROOM_ID = 1829181560


def room_root(tmp_path):
    root = tmp_path / 'BililiveRecorder'
    (root / str(ROOM_ID)).mkdir(parents=True)
    return root


def test_dry_run_does_not_initialize_youtube_or_write_journal(monkeypatch, tmp_path):
    root = room_root(tmp_path)
    video = root / str(ROOM_ID) / '2026-07-28 19:00:00.flv'
    video.write_bytes(b'baseline')

    def fail_youtube_init(config):
        raise AssertionError('YouTube client must not initialize in dry-run')

    monkeypatch.setattr(
        'recorder.utils.bililive_directory_monitor.Youtube',
        fail_youtube_init,
    )
    state_dir = tmp_path / 'state'

    result = run_monitor(
        root=str(root),
        room_id=ROOM_ID,
        api_url='http://127.0.0.1:2356',
        state_dir=str(state_dir),
        dry_run=True,
        once=True,
        room_state_provider=lambda: RoomState(False, False),
    )

    assert result == 0
    assert not (state_dir / 'state.jsonl').exists()


def test_dry_run_does_not_probe_or_parse_xml_while_gate_is_closed(
    monkeypatch, tmp_path
):
    root = room_root(tmp_path)
    monkeypatch.setattr(
        'recorder.utils.bililive_directory_monitor._dry_run_media_report',
        lambda *args: (_ for _ in ()).throw(
            AssertionError('active room must block probe and XML work')
        ),
    )

    result = run_monitor(
        root=str(root), room_id=ROOM_ID,
        api_url='http://127.0.0.1:2356', state_dir=str(tmp_path / 'state'),
        dry_run=True, once=True,
        room_state_provider=lambda: RoomState(True, False),
    )

    assert result == 0


def test_dry_run_media_report_does_not_probe_baseline_only_flv(
    monkeypatch, tmp_path
):
    video = tmp_path / 'baseline.flv'
    video.write_bytes(b'fixture')
    calls = []

    def fail_after_recording(path):
        calls.append(path)
        raise RuntimeError('probe fixture')

    monkeypatch.setattr(
        'recorder.utils.bililive_directory_monitor.inspect_media',
        fail_after_recording,
    )

    _dry_run_media_report(
        SimpleNamespace(manifests=()),
        MonitorDecision(
            state=SessionState.WAITING,
            baseline_paths=(str(video),),
        ),
    )

    assert calls == []


def test_once_performs_exactly_one_observation_without_sleep(monkeypatch, tmp_path):
    root = room_root(tmp_path)
    calls = []

    monkeypatch.setattr(
        'recorder.utils.bililive_directory_monitor.Youtube', lambda config: object()
    )
    monkeypatch.setattr(
        'recorder.utils.bililive_directory_monitor.time',
        SimpleNamespace(sleep=lambda seconds: (_ for _ in ()).throw(
            AssertionError(f'unexpected sleep {seconds}')
        )),
    )

    result = run_monitor(
        root=str(root),
        room_id=ROOM_ID,
        api_url='http://127.0.0.1:2356',
        state_dir=str(tmp_path / 'state'),
        once=True,
        room_state_provider=lambda: calls.append('observe') or RoomState(False, False),
    )

    assert result == 0
    assert calls == ['observe']


def test_api_failure_is_wait_only_and_does_not_run_cleanup_or_publish(
    monkeypatch, tmp_path
):
    root = room_root(tmp_path)

    class FailRunner:
        def __init__(self, *args, **kwargs):
            pass

        def run_pending_once(self, replay):
            raise AssertionError('unavailable API must block publication')

    class FailCleanup:
        def __init__(self, *args, **kwargs):
            pass

        def run(self, states, dry_run):
            raise AssertionError('unavailable API must block cleanup')

    monkeypatch.setattr(
        'recorder.utils.bililive_directory_monitor.Youtube', lambda config: object()
    )
    monkeypatch.setattr(
        'recorder.utils.bililive_directory_monitor.BililivePublishRunner', FailRunner
    )
    monkeypatch.setattr(
        'recorder.utils.bililive_directory_monitor.StateAwareCleanup', FailCleanup
    )

    result = run_monitor(
        root=str(root),
        room_id=ROOM_ID,
        api_url='http://127.0.0.1:2356',
        state_dir=str(tmp_path / 'state'),
        once=True,
        room_state_provider=lambda: (_ for _ in ()).throw(OSError('offline')),
    )

    assert result == 0


def test_default_state_directory_is_under_recorder_base_path(monkeypatch, tmp_path):
    root = room_root(tmp_path)
    monkeypatch.setattr('recorder.base_path', tmp_path)
    monkeypatch.setattr(
        'recorder.utils.bililive_directory_monitor.Youtube', lambda config: object()
    )

    result = run_monitor(
        root=str(root),
        room_id=ROOM_ID,
        api_url='http://127.0.0.1:2356',
        once=True,
        room_state_provider=lambda: RoomState(False, False),
    )

    assert result == 0
    assert (tmp_path / 'var' / 'bililive' / str(ROOM_ID) / 'state.jsonl').is_file()


def test_corrupt_middle_journal_fails_before_youtube_or_cleanup_init(
    monkeypatch, tmp_path
):
    root = room_root(tmp_path)
    state_dir = tmp_path / 'state'
    state_dir.mkdir()
    (state_dir / 'state.jsonl').write_text(
        '{"event":"initialized"}\nnot-json\n{"event":"initialized"}\n'
    )

    monkeypatch.setattr(
        'recorder.utils.bililive_directory_monitor.Youtube',
        lambda config: (_ for _ in ()).throw(AssertionError('YouTube initialized')),
    )
    monkeypatch.setattr(
        'recorder.utils.bililive_directory_monitor.StateAwareCleanup',
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError('cleanup initialized')),
    )

    result = run_monitor(
        root=str(root),
        room_id=ROOM_ID,
        api_url='http://127.0.0.1:2356',
        state_dir=str(state_dir),
        once=True,
        room_state_provider=lambda: RoomState(False, False),
    )

    assert result != 0


def test_http_provider_uses_expected_endpoint_and_rejects_non_boolean_state(
    monkeypatch, tmp_path
):
    root = room_root(tmp_path)
    calls = []

    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {'recording': 0, 'streaming': False}

    class Client:
        def __init__(self, timeout):
            calls.append(('timeout', timeout))

        def get(self, url):
            calls.append(('get', url))
            return Response()

        def close(self):
            calls.append(('close',))

    monkeypatch.setattr('recorder.utils.bililive_directory_monitor.httpx.Client', Client)

    result = run_monitor(
        root=str(root),
        room_id=ROOM_ID,
        api_url='http://127.0.0.1:2356/',
        state_dir=str(tmp_path / 'state'),
        dry_run=True,
        once=True,
    )

    assert result == 0
    assert calls == [
        ('timeout', 5),
        ('get', f'http://127.0.0.1:2356/api/room/{ROOM_ID}'),
        ('close',),
    ]


def test_room_directory_must_exist(tmp_path):
    root = tmp_path / 'BililiveRecorder'
    root.mkdir()

    result = run_monitor(
        root=str(root), room_id=ROOM_ID,
        api_url='http://127.0.0.1:2356', dry_run=True, once=True,
        room_state_provider=lambda: RoomState(False, False),
    )

    assert result != 0


def test_process_lock_is_held_until_worker_stops(monkeypatch, tmp_path):
    root = room_root(tmp_path)
    state_dir = tmp_path / 'state'

    class Service:
        def __init__(self, **kwargs):
            pass

        def start(self):
            pass

        def observe_once(self):
            pass

        def stop(self):
            with pytest.raises(AlreadyRunningError):
                ProcessLock(state_dir)

    monkeypatch.setattr(
        'recorder.utils.bililive_directory_monitor.Youtube', lambda config: object()
    )
    monkeypatch.setattr(
        'recorder.utils.bililive_directory_monitor.BililiveDirectoryService', Service
    )

    result = run_monitor(
        root=str(root), room_id=ROOM_ID,
        api_url='http://127.0.0.1:2356', state_dir=str(state_dir), once=True,
        room_state_provider=lambda: RoomState(False, False),
    )

    assert result == 0


def test_lock_contention_returns_nonzero_startup_result(tmp_path):
    root = room_root(tmp_path)
    state_dir = tmp_path / 'state'

    with ProcessLock(state_dir):
        result = run_monitor(
            root=str(root), room_id=ROOM_ID,
            api_url='http://127.0.0.1:2356', state_dir=str(state_dir),
            dry_run=True, once=True,
            room_state_provider=lambda: RoomState(False, False),
        )

    assert result != 0

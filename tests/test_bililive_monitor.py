from datetime import datetime, timedelta, timezone

import pytest

from recorder.bililive.journal import JsonlJournal, baseline_fingerprint
from recorder.bililive.models import RoomState, SessionState
from recorder.bililive.monitor import (
    QUIET_PERIOD_SECONDS,
    BililiveSessionMonitor,
    SessionMonitorState,
)


UTC = timezone.utc


def at(hour, minute=0):
    return datetime(2026, 7, 27, hour, minute, tzinfo=UTC)


def armed_machine(ids=None):
    values = iter(ids or ('session-1', 'session-2'))
    return SessionMonitorState(initialized=True, id_factory=lambda: next(values))


def test_first_offline_observation_baselines_every_path_and_arms():
    machine = SessionMonitorState(initialized=False)
    snapshot = {'/recording/a.flv': (100, 1), '/recording/a.xml': (20, 2)}

    decision = machine.observe(at(18), RoomState(False, False), snapshot)

    assert decision.state is SessionState.WAITING
    assert decision.baseline_paths == tuple(sorted(snapshot))
    assert decision.ready_paths == ()
    assert machine.initialized is True


def test_first_start_while_live_skips_entire_current_session():
    machine = SessionMonitorState(
        initialized=False, id_factory=lambda: 'skipped-session'
    )

    first = machine.observe(
        at(18), RoomState(True, True), {'a.flv': (100, 1)}
    )
    during = machine.observe(
        at(21),
        RoomState(True, True),
        {'a.flv': (200, 2), 'b.flv': (100, 1)},
    )
    settled = machine.observe(
        at(22, 31),
        RoomState(False, False),
        {'a.flv': (200, 2), 'b.flv': (100, 1)},
    )

    assert first.state is SessionState.SKIP_CURRENT_SESSION
    assert first.session_id == 'skipped-session'
    assert set(during.baseline_paths) == {'a.flv', 'b.flv'}
    assert settled.state is SessionState.WAITING
    assert settled.ready_paths == ()
    assert set(settled.baseline_paths) == {'a.flv', 'b.flv'}


def test_offline_session_requires_thirty_unchanged_minutes():
    machine = armed_machine()
    machine.observe(at(18), RoomState(True, True), {'a.flv': (100, 1)})
    machine.observe(at(22), RoomState(False, False), {'a.flv': (200, 2)})

    early = machine.observe(
        at(22, 29), RoomState(False, False), {'a.flv': (200, 2)}
    )
    ready = machine.observe(
        at(22, 30), RoomState(False, False), {'a.flv': (200, 2)}
    )

    assert early.state is SessionState.SETTLING
    assert ready.state is SessionState.READY
    assert ready.ready_paths == ('a.flv',)


def test_api_unavailable_never_advances_settling_to_ready():
    machine = armed_machine()
    machine.observe(at(18), RoomState(True, True), {'a.flv': (100, 1)})
    machine.observe(at(22), RoomState(False, False), {'a.flv': (200, 2)})

    unavailable = machine.observe(at(23), None, {'a.flv': (200, 2)})

    assert unavailable.state is SessionState.SETTLING
    assert unavailable.ready_paths == ()
    assert unavailable.reason == 'room state unavailable'


def test_any_flv_or_xml_snapshot_change_resets_quiet_period():
    machine = armed_machine()
    machine.observe(
        at(18),
        RoomState(True, True),
        {'a.flv': (100, 1), 'a.xml': (10, 1)},
    )
    machine.observe(
        at(22),
        RoomState(False, False),
        {'a.flv': (200, 2), 'a.xml': (20, 2)},
    )

    changed = machine.observe(
        at(22, 29),
        RoomState(False, False),
        {'a.flv': (200, 2), 'a.xml': (21, 3)},
    )
    too_early = machine.observe(
        at(22, 30),
        RoomState(False, False),
        {'a.flv': (200, 2), 'a.xml': (21, 3)},
    )

    assert changed.quiet_since == at(22, 29)
    assert too_early.state is SessionState.SETTLING
    assert set(too_early.session_paths) == {'a.flv', 'a.xml'}


def test_recording_accumulates_only_paths_changed_since_waiting_snapshot():
    machine = armed_machine(ids=('stable-id',))
    waiting = {
        'old.flv': (100, 1),
        'changed.xml': (10, 1),
    }
    machine.observe(at(17), RoomState(False, False), waiting)

    started = machine.observe(
        at(18),
        RoomState(True, True),
        {
            'old.flv': (100, 1),
            'changed.xml': (11, 2),
            'new.flv': (50, 1),
        },
    )
    continued = machine.observe(
        at(19),
        RoomState(True, True),
        {
            'old.flv': (100, 1),
            'changed.xml': (12, 3),
            'new.flv': (100, 2),
            'new.xml': (10, 1),
        },
    )

    assert started.session_id == continued.session_id == 'stable-id'
    assert set(continued.session_paths) == {
        'changed.xml',
        'new.flv',
        'new.xml',
    }
    assert 'old.flv' not in continued.session_paths


def test_restored_settling_session_waits_a_fresh_quiet_period(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('initialized')
    journal.append(
        'session_state',
        state='settling',
        session_id='stable-id',
        session_paths=('a.flv',),
        snapshot={'a.flv': (200, 2)},
        quiet_since=at(21).isoformat(),
        started_at=at(18).isoformat(),
    )
    machine = SessionMonitorState.restore(journal.replay())

    first = machine.observe(
        at(23), RoomState(False, False), {'a.flv': (200, 2)}
    )
    early = machine.observe(
        at(23, 29), RoomState(False, False), {'a.flv': (200, 2)}
    )
    ready = machine.observe(
        at(23, 30), RoomState(False, False), {'a.flv': (200, 2)}
    )

    assert first.session_id == 'stable-id'
    assert first.quiet_since == at(23)
    assert early.state is SessionState.SETTLING
    assert ready.state is SessionState.READY


def test_restored_recording_keeps_session_id_and_accumulated_paths(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('initialized')
    journal.append(
        'session_state',
        state='recording',
        session_id='persisted-id',
        session_paths=('a.flv', 'a.xml'),
        snapshot={'a.flv': (100, 1), 'a.xml': (10, 1)},
        quiet_since=at(18).isoformat(),
        started_at=at(18).isoformat(),
    )

    restored = SessionMonitorState.restore(journal.replay())
    decision = restored.observe(
        at(19),
        RoomState(True, True),
        {'a.flv': (200, 2), 'a.xml': (20, 2), 'b.flv': (50, 1)},
    )

    assert decision.session_id == 'persisted-id'
    assert set(decision.session_paths) == {'a.flv', 'a.xml', 'b.flv'}


def test_restored_recording_cannot_count_downtime_as_quiet_time(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('initialized')
    journal.append(
        'session_state',
        state='recording',
        session_id='persisted-id',
        session_paths=('a.flv',),
        snapshot={'a.flv': (200, 2)},
        quiet_since=at(18).isoformat(),
        started_at=at(18).isoformat(),
    )
    machine = SessionMonitorState.restore(journal.replay())

    first = machine.observe(
        at(23), RoomState(False, False), {'a.flv': (200, 2)}
    )
    early = machine.observe(
        at(23, 29), RoomState(False, False), {'a.flv': (200, 2)}
    )

    assert first.state is SessionState.SETTLING
    assert first.quiet_since == at(23)
    assert early.state is SessionState.SETTLING


def test_journaled_offline_baseline_marks_initialized_only_after_file_events(
    tmp_path,
):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    monitor = BililiveSessionMonitor(journal=journal, room_id=123)
    snapshot = {'/recording/a.flv': (100, 1), '/recording/a.xml': (20, 2)}

    decision = monitor.observe(at(18), RoomState(False, False), snapshot)
    replay = journal.replay()
    events = [line['event'] for line in _journal_records(journal.path)]

    assert decision.state is SessionState.WAITING
    assert replay.initialized is True
    assert replay.session.state is SessionState.WAITING
    assert events[-1] == 'initialized'
    assert events[:2] == ['baseline', 'baseline']
    assert set(replay.files) == {
        baseline_fingerprint(path, *identity)
        for path, identity in snapshot.items()
    }


def test_live_first_run_defers_baselines_until_offline_and_quiet(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    monitor = BililiveSessionMonitor(
        journal=journal, room_id=123, id_factory=lambda: 'skip-id'
    )

    monitor.observe(at(18), RoomState(True, True), {'a.flv': (100, 1)})
    monitor.observe(
        at(21),
        RoomState(True, True),
        {'a.flv': (200, 2), 'b.flv': (100, 1)},
    )

    before = journal.replay()
    assert before.initialized is False
    assert before.files == {}
    assert before.session.state is SessionState.SKIP_CURRENT_SESSION

    settled = monitor.observe(
        at(22, 31),
        RoomState(False, False),
        {'a.flv': (200, 2), 'b.flv': (100, 1)},
    )
    after = journal.replay()

    assert settled.state is SessionState.WAITING
    assert after.initialized is True
    assert len(after.files) == 2
    assert after.session.state is SessionState.WAITING


def test_failed_baseline_persistence_does_not_leave_monitor_armed(tmp_path):
    class FailingJournal(JsonlJournal):
        def append(self, event, **fields):
            if event == 'baseline':
                raise OSError('disk unavailable')
            return super().append(event, **fields)

    journal = FailingJournal(tmp_path / 'state.jsonl')
    monitor = BililiveSessionMonitor(journal=journal, room_id=123)

    with pytest.raises(OSError, match='disk unavailable'):
        monitor.observe(
            at(18), RoomState(False, False), {'a.flv': (100, 1)}
        )

    assert monitor.machine.initialized is False
    assert monitor.machine.state is SessionState.BASELINING


def test_manifest_is_durable_before_monitor_rearms(tmp_path):
    events = []
    monitor_ref = {}

    class ObservingJournal(JsonlJournal):
        def append(inner_self, event, **fields):
            monitor = monitor_ref.get('monitor')
            events.append(
                (event, monitor.machine.state if monitor is not None else None)
            )
            return super().append(event, **fields)

    journal = ObservingJournal(tmp_path / 'state.jsonl')
    journal.append('initialized')
    monitor = BililiveSessionMonitor(
        journal=journal,
        room_id=123,
        machine=armed_machine(ids=('session-1',)),
    )
    monitor_ref['monitor'] = monitor
    monitor.observe(at(18), RoomState(True, True), {'a.flv': (100, 1)})
    monitor.observe(at(22), RoomState(False, False), {'a.flv': (200, 2)})

    decision = monitor.observe(
        at(22, 30), RoomState(False, False), {'a.flv': (200, 2)}
    )

    replay = journal.replay()
    manifest_event = next(
        item for item in events if item[0] == 'session_manifest_ready'
    )
    assert manifest_event == ('session_manifest_ready', SessionState.READY)
    assert decision.state is SessionState.READY
    assert monitor.machine.state is SessionState.WAITING
    assert replay.session.state is SessionState.WAITING
    assert replay.manifests[0].manifest_id == 'session-1'
    assert replay.manifests[0].flv_paths == ('a.flv',)


def test_journal_retains_multiple_ready_manifests(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('initialized')
    monitor = BililiveSessionMonitor(
        journal=journal,
        room_id=123,
        machine=armed_machine(ids=('session-1', 'session-2')),
    )

    for offset, path in enumerate(('a.flv', 'b.flv')):
        start = at(18) + timedelta(days=offset)
        monitor.observe(start, RoomState(True, True), {path: (100, 1)})
        monitor.observe(
            start + timedelta(hours=4),
            RoomState(False, False),
            {path: (200, 2)},
        )
        monitor.observe(
            start + timedelta(hours=4, seconds=QUIET_PERIOD_SECONDS),
            RoomState(False, False),
            {path: (200, 2)},
        )

    replay = journal.replay()
    assert [manifest.manifest_id for manifest in replay.manifests] == [
        'session-1',
        'session-2',
    ]


def test_restart_after_manifest_fsync_does_not_emit_conflicting_manifest(
    tmp_path,
):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('initialized')
    journal.append(
        'session_state',
        state='settling',
        session_id='session-1',
        session_paths=('a.flv',),
        snapshot={'a.flv': (200, 2)},
        quiet_since=at(22).isoformat(),
        started_at=at(18).isoformat(),
    )
    journal.append(
        'session_manifest_ready',
        manifest_id='session-1',
        room_id=123,
        started_at=at(18).isoformat(),
        settled_at=at(22, 30).isoformat(),
        flv_paths=('a.flv',),
    )

    restarted = BililiveSessionMonitor(journal=journal, room_id=123)
    decision = restarted.observe(
        at(23), RoomState(False, False), {'a.flv': (200, 2)}
    )

    assert decision.state is SessionState.WAITING
    assert restarted.machine.state is SessionState.WAITING
    assert len(journal.replay().manifests) == 1


def test_observe_rejects_naive_time_without_mutating_state():
    machine = armed_machine()

    with pytest.raises(ValueError, match='timezone-aware'):
        machine.observe(
            datetime(2026, 7, 27, 18),
            RoomState(False, False),
            {'a.flv': (100, 1)},
        )

    assert machine.state is SessionState.WAITING
    assert machine.snapshot == {}


def _journal_records(path):
    import json

    return [json.loads(line) for line in path.read_text().splitlines()]

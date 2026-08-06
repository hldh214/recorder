import json
from datetime import datetime, timedelta, timezone

import pytest

from recorder.bililive.journal import JsonlJournal, baseline_fingerprint
from recorder.bililive.models import (
    JournalManifest,
    JournalReplay,
    JournalSessionState,
    RoomState,
    SessionState,
)
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


def append_pending_resettle(
    journal, video, manifest_id='old-session', settled_at=None
):
    settled_at = settled_at or at(12)
    journal.append(
        'session_manifest_ready',
        manifest_id=manifest_id,
        room_id=123,
        started_at=at(8).isoformat(),
        settled_at=settled_at.isoformat(),
        flv_paths=(video,),
        snapshot={video: (100, 1)},
    )
    journal.append(
        'session_manifest_changed',
        manifest_id=manifest_id,
        detected_at=(settled_at + timedelta(minutes=5)).isoformat(),
        reason='frozen identity changed',
        changed_paths=(video,),
    )


def snapshot_identity(instant, size=100):
    return size, int(instant.timestamp() * 1_000_000_000)


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


def test_api_unavailable_invalidates_existing_quiet_proof():
    machine = armed_machine()
    machine.observe(at(18), RoomState(True, True), {'a.flv': (100, 1)})
    machine.observe(at(22), RoomState(False, False), {'a.flv': (200, 2)})
    machine.observe(at(22, 20), None, {'a.flv': (200, 2)})

    restored_proof = machine.observe(
        at(22, 40), RoomState(False, False), {'a.flv': (200, 2)}
    )
    early = machine.observe(
        at(23, 9), RoomState(False, False), {'a.flv': (200, 2)}
    )
    ready = machine.observe(
        at(23, 10), RoomState(False, False), {'a.flv': (200, 2)}
    )

    assert restored_proof.quiet_since == at(22, 40)
    assert early.state is SessionState.SETTLING
    assert ready.state is SessionState.READY


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
        room_id=123,
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
        room_id=123,
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
        room_id=123,
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
    assert replay.session.room_id == 123
    assert replay.session.state is SessionState.WAITING
    assert events == [
        'session_state',
        'baseline',
        'baseline',
        'session_state',
        'initialized',
    ]
    ownership = _journal_records(journal.path)[0]
    assert ownership['room_id'] == 123
    assert ownership['state'] == SessionState.BASELINING
    assert ownership['session_id'] is None
    assert ownership['snapshot'] == {
        '/recording/a.flv': [100, 1],
        '/recording/a.xml': [20, 2],
    }
    assert set(replay.files) == {
        baseline_fingerprint(path, *identity)
        for path, identity in snapshot.items()
    }


def test_monitor_rejects_configured_room_mismatch_with_waiting_state(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
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

    with pytest.raises(ValueError, match='room_id'):
        BililiveSessionMonitor(journal=journal, room_id=456)


def test_monitor_checks_retained_completed_manifest_room_with_injected_machine(
    tmp_path,
):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    video = str(tmp_path / 'video.flv')
    journal.append(
        'session_manifest_ready',
        manifest_id='old-session',
        room_id=456,
        started_at=at(18).isoformat(),
        settled_at=at(22, 30).isoformat(),
        flv_paths=(video,),
        snapshot={video: (200, 2)},
    )
    journal.append(
        'session_manifest_completed', manifest_id='old-session'
    )

    with pytest.raises(ValueError, match='room_id'):
        BililiveSessionMonitor(
            journal=journal, room_id=123, machine=armed_machine()
        )


def test_monitor_replays_journal_once_when_machine_is_injected(tmp_path):
    class CountingJournal(JsonlJournal):
        def __init__(self, path):
            super().__init__(path)
            self.replay_calls = 0

        def replay(self):
            self.replay_calls += 1
            return super().replay()

    journal = CountingJournal(tmp_path / 'state.jsonl')

    BililiveSessionMonitor(
        journal=journal, room_id=123, machine=armed_machine()
    )

    assert journal.replay_calls == 1


@pytest.mark.parametrize(
    ('target_event', 'occurrence', 'after_write'),
    [
        ('baseline', 1, False),
        ('baseline', 2, False),
        ('session_state', 2, True),
        ('initialized', 1, False),
    ],
    ids=[
        'after-ownership',
        'mid-baseline',
        'after-completion-state',
        'before-initialized',
    ],
)
def test_offline_baseline_crash_recovery_preserves_room_ownership(
    tmp_path, target_event, occurrence, after_write
):
    class FaultJournal(JsonlJournal):
        def __init__(self, path):
            super().__init__(path)
            self.counts = {}

        def append(self, event, **fields):
            self.counts[event] = self.counts.get(event, 0) + 1
            triggered = (
                event == target_event
                and self.counts[event] == occurrence
            )
            if triggered and not after_write:
                raise OSError('simulated crash')
            result = super().append(event, **fields)
            if triggered:
                raise OSError('simulated crash')
            return result

    path = tmp_path / 'state.jsonl'
    snapshot = {
        '/recording/a.flv': (100, 1),
        '/recording/a.xml': (20, 2),
    }
    monitor = BililiveSessionMonitor(
        journal=FaultJournal(path), room_id=123
    )

    with pytest.raises(OSError, match='simulated crash'):
        monitor.observe(at(18), RoomState(False, False), snapshot)

    interrupted = JsonlJournal(path).replay()
    records = _journal_records(path)
    assert interrupted.initialized is False
    assert records[0]['event'] == 'session_state'
    assert records[0]['state'] == SessionState.BASELINING
    assert records[0]['room_id'] == 123
    with pytest.raises(ValueError, match='room_id'):
        BililiveSessionMonitor(journal=JsonlJournal(path), room_id=456)

    recovered = BililiveSessionMonitor(
        journal=JsonlJournal(path), room_id=123
    )
    decision = recovered.observe(
        at(19), RoomState(False, False), snapshot
    )
    replay = JsonlJournal(path).replay()

    assert decision.state is SessionState.WAITING
    assert replay.initialized is True
    assert replay.session.state is SessionState.WAITING
    assert replay.session.room_id == 123
    assert len(replay.files) == len(snapshot)


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
    assert before.session.room_id == 123
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


def test_failed_persistence_rollback_uses_configured_room_id(
    tmp_path, monkeypatch
):
    calls = []
    original_restore = SessionMonitorState.restore.__func__

    def tracking_restore(cls, replay, id_factory=None, room_id=None):
        calls.append(room_id)
        return original_restore(
            cls, replay, id_factory=id_factory, room_id=room_id
        )

    monkeypatch.setattr(
        SessionMonitorState, 'restore', classmethod(tracking_restore)
    )

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

    assert calls == [123, 123]


def test_manifest_is_durable_before_monitor_rearms(tmp_path):
    events = []
    monitor_ref = {}
    video = str(tmp_path / 'a.flv')
    xml = str(tmp_path / 'a.xml')
    unrelated = str(tmp_path / 'historical.flv')

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
    monitor.observe(
        at(17), RoomState(False, False), {unrelated: (500, 5)}
    )
    monitor.observe(
        at(18),
        RoomState(True, True),
        {video: (100, 1), xml: (10, 1), unrelated: (500, 5)},
    )
    monitor.observe(
        at(22),
        RoomState(False, False),
        {video: (200, 2), xml: (20, 2), unrelated: (500, 5)},
    )

    decision = monitor.observe(
        at(22, 30),
        RoomState(False, False),
        {video: (200, 2), xml: (20, 2), unrelated: (500, 5)},
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
    assert replay.manifests[0].flv_paths == (video,)
    assert replay.manifests[0].snapshot == {
        video: (200, 2),
        xml: (20, 2),
    }


def test_journaled_monitor_fails_closed_on_relative_manifest_path(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('initialized')
    monitor = BililiveSessionMonitor(
        journal=journal,
        room_id=123,
        machine=armed_machine(ids=('session-1',)),
    )
    monitor.observe(at(18), RoomState(True, True), {'a.flv': (100, 1)})
    monitor.observe(at(22), RoomState(False, False), {'a.flv': (200, 2)})

    with pytest.raises(ValueError, match='normalized absolute'):
        monitor.observe(
            at(22, 30), RoomState(False, False), {'a.flv': (200, 2)}
        )

    assert journal.replay().manifests == ()
    assert monitor.machine.state is SessionState.SETTLING


def test_ready_session_without_flv_rearms_without_empty_manifest(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('initialized')
    monitor = BililiveSessionMonitor(
        journal=journal,
        room_id=123,
        machine=armed_machine(ids=('xml-only',)),
    )
    monitor.observe(at(18), RoomState(True, True), {'a.xml': (10, 1)})
    monitor.observe(at(22), RoomState(False, False), {'a.xml': (20, 2)})

    decision = monitor.observe(
        at(22, 30), RoomState(False, False), {'a.xml': (20, 2)}
    )

    assert decision.state is SessionState.READY
    assert decision.ready_paths == ()
    assert monitor.machine.state is SessionState.WAITING
    assert journal.replay().manifests == ()
    assert journal.replay().session.state is SessionState.WAITING


def test_live_segment_manifest_excludes_current_flv_and_leaves_tail(tmp_path):
    first = str(tmp_path / 'first.flv')
    current = str(tmp_path / 'current.flv')
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('initialized')
    ids = iter(('stream-session', 'first-segment'))
    monitor = BililiveSessionMonitor(
        journal=journal,
        room_id=123,
        id_factory=lambda: next(ids),
        live_segment_manifests=True,
    )

    monitor.observe(
        at(8),
        RoomState(True, True),
        {first: snapshot_identity(at(8))},
    )
    recording = monitor.observe(
        at(11),
        RoomState(True, True),
        {
            first: snapshot_identity(at(10, 30)),
            current: snapshot_identity(at(11)),
        },
    )

    assert recording.state is SessionState.RECORDING
    replay = journal.replay()
    assert [manifest.flv_paths for manifest in replay.manifests] == [
        (first,),
    ]

    monitor.observe(
        at(11, 10),
        RoomState(False, False),
        {
            first: snapshot_identity(at(10, 30)),
            current: snapshot_identity(at(11)),
        },
    )
    finished = monitor.observe(
        at(11, 40),
        RoomState(False, False),
        {
            first: snapshot_identity(at(10, 30)),
            current: snapshot_identity(at(11)),
        },
    )

    assert finished.state is SessionState.READY
    assert [manifest.flv_paths for manifest in journal.replay().manifests] == [
        (first,), (current,),
    ]


def test_journal_retains_multiple_ready_manifests(tmp_path):
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('initialized')
    monitor = BililiveSessionMonitor(
        journal=journal,
        room_id=123,
        machine=armed_machine(ids=('session-1', 'session-2')),
    )

    paths = tuple(str(tmp_path / name) for name in ('a.flv', 'b.flv'))
    for offset, path in enumerate(paths):
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
    video = str(tmp_path / 'a.flv')
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('initialized')
    journal.append(
        'session_state',
        room_id=123,
        state='settling',
        session_id='session-1',
        session_paths=(video,),
        snapshot={video: (200, 2)},
        quiet_since=at(22).isoformat(),
        started_at=at(18).isoformat(),
    )
    journal.append(
        'session_manifest_ready',
        manifest_id='session-1',
        room_id=123,
        started_at=at(18).isoformat(),
        settled_at=at(22, 30).isoformat(),
        flv_paths=(video,),
        snapshot={video: (200, 2)},
    )

    restarted = BililiveSessionMonitor(journal=journal, room_id=123)
    decision = restarted.observe(
        at(23), RoomState(False, False), {video: (200, 2)}
    )

    assert decision.state is SessionState.WAITING
    assert restarted.machine.state is SessionState.WAITING
    assert len(journal.replay().manifests) == 1


def test_offline_pending_resettle_claims_and_waits_fresh_quiet_period(tmp_path):
    video = str(tmp_path / 'video.flv')
    xml = str(tmp_path / 'video.xml')
    unrelated = str(tmp_path / 'unrelated.flv')
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('initialized')
    journal.append(
        'session_state',
        room_id=123,
        state='waiting',
        session_id=None,
        session_paths=(),
        snapshot={video: (100, 1)},
        quiet_since=None,
        started_at=None,
    )
    append_pending_resettle(journal, video)
    snapshot = {
        video: (200, 2),
        xml: (20, 2),
        unrelated: (900, 9),
    }
    monitor = BililiveSessionMonitor(
        journal=journal,
        room_id=123,
        id_factory=lambda: 'replacement-session',
    )

    claimed = monitor.observe(at(13), RoomState(False, False), snapshot)
    early = monitor.observe(at(13, 29), RoomState(False, False), snapshot)
    ready = monitor.observe(at(13, 30), RoomState(False, False), snapshot)

    assert claimed.state is SessionState.SETTLING
    assert claimed.session_id == 'replacement-session'
    assert claimed.quiet_since == at(13)
    assert claimed.started_at == at(8)
    assert set(claimed.session_paths) == {video, xml}
    assert dict(claimed.snapshot) == snapshot
    assert early.state is SessionState.SETTLING
    assert ready.state is SessionState.READY
    replay = journal.replay()
    assert replay.pending_resettles == ()
    old, replacement = replay.manifests
    assert old.manifest_id == 'old-session'
    assert old.invalidated is True
    assert old.replacement_manifest_id == 'replacement-session'
    assert dict(old.snapshot) == {video: (100, 1)}
    assert replacement.manifest_id == 'replacement-session'
    assert replacement.started_at == at(8).isoformat()
    assert replacement.snapshot == {video: (200, 2), xml: (20, 2)}


def test_active_pending_resettle_claims_as_recording(tmp_path):
    video = str(tmp_path / 'video.flv')
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('initialized')
    journal.append(
        'session_state',
        room_id=123,
        state='waiting',
        session_id=None,
        session_paths=(),
        snapshot={video: (100, 1)},
        quiet_since=None,
        started_at=None,
    )
    append_pending_resettle(journal, video)
    monitor = BililiveSessionMonitor(
        journal=journal,
        room_id=123,
        id_factory=lambda: 'replacement-session',
    )

    decision = monitor.observe(
        at(13), RoomState(True, True), {video: (200, 2)}
    )

    assert decision.state is SessionState.RECORDING
    assert decision.quiet_since == at(13)
    replay = journal.replay()
    assert replay.session.state is SessionState.RECORDING
    assert replay.pending_resettles == ()
    assert replay.manifests[0].replacement_manifest_id == (
        'replacement-session'
    )


def test_active_resettle_claim_includes_fragments_changed_since_waiting(
    tmp_path,
):
    video = str(tmp_path / 'video.flv')
    fragment = str(tmp_path / 'fragment.flv')
    fragment_xml = str(tmp_path / 'fragment.xml')
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('initialized')
    journal.append(
        'session_state',
        room_id=123,
        state='waiting',
        session_id=None,
        session_paths=(),
        snapshot={video: (100, 1), fragment: (50, 1)},
        quiet_since=None,
        started_at=None,
    )
    append_pending_resettle(journal, video)
    monitor = BililiveSessionMonitor(
        journal=journal,
        room_id=123,
        id_factory=lambda: 'replacement-session',
    )
    current = {
        video: (200, 2),
        fragment: (75, 2),
        fragment_xml: (10, 2),
        str(tmp_path / 'unrelated.txt'): (3, 1),
    }

    decision = monitor.observe(at(13), RoomState(True, True), current)

    assert decision.state is SessionState.RECORDING
    assert set(decision.session_paths) == {video, fragment, fragment_xml}
    assert dict(decision.snapshot) == current
    replay = journal.replay()
    assert set(replay.session.session_paths) == {
        video, fragment, fragment_xml
    }


def test_resettle_claim_recovers_after_durable_append_then_error(tmp_path):
    class DurableThenErrorJournal(JsonlJournal):
        def __init__(self, path):
            super().__init__(path)
            self.failed = False

        def append(self, event, **fields):
            result = super().append(event, **fields)
            if event == 'session_resettle_started' and not self.failed:
                self.failed = True
                raise OSError('simulated post-fsync failure')
            return result

    video = str(tmp_path / 'video.flv')
    path = tmp_path / 'state.jsonl'
    journal = DurableThenErrorJournal(path)
    journal.append('initialized')
    journal.append(
        'session_state',
        room_id=123,
        state='waiting',
        session_id=None,
        session_paths=(),
        snapshot={video: (100, 1)},
        quiet_since=None,
        started_at=None,
    )
    append_pending_resettle(journal, video)
    monitor = BililiveSessionMonitor(
        journal=journal,
        room_id=123,
        id_factory=lambda: 'replacement-session',
    )
    current = {video: (200, 2)}

    with pytest.raises(OSError, match='post-fsync'):
        monitor.observe(at(13), RoomState(True, True), current)

    assert monitor.machine.state is SessionState.RECORDING
    assert monitor.machine.session_id == 'replacement-session'
    assert journal.replay().pending_resettles == ()

    resumed = monitor.observe(at(13, 1), RoomState(True, True), current)
    assert resumed.session_id == 'replacement-session'
    restarted = BililiveSessionMonitor(
        journal=JsonlJournal(path),
        room_id=123,
        id_factory=lambda: pytest.fail('must not allocate another session'),
    )
    restarted_decision = restarted.observe(
        at(13, 2), RoomState(True, True), current
    )
    assert restarted_decision.session_id == 'replacement-session'
    assert sum(
        record['event'] == 'session_resettle_started'
        for record in _journal_records(path)
    ) == 1


def test_active_resettle_starts_fresh_quiet_period_when_room_goes_offline(
    tmp_path,
):
    video = str(tmp_path / 'video.flv')
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('initialized')
    journal.append(
        'session_state',
        room_id=123,
        state='waiting',
        session_id=None,
        session_paths=(),
        snapshot={video: (100, 1)},
        quiet_since=None,
        started_at=None,
    )
    append_pending_resettle(journal, video)
    monitor = BililiveSessionMonitor(
        journal=journal,
        room_id=123,
        id_factory=lambda: 'replacement-session',
    )
    snapshot = {video: (200, 2)}

    monitor.observe(at(13), RoomState(True, True), snapshot)
    offline = monitor.observe(at(14), RoomState(False, False), snapshot)
    early = monitor.observe(at(14, 29), RoomState(False, False), snapshot)
    ready = monitor.observe(at(14, 30), RoomState(False, False), snapshot)

    assert offline.state is SessionState.SETTLING
    assert offline.quiet_since == at(14)
    assert early.state is SessionState.SETTLING
    assert ready.state is SessionState.READY


def test_restart_after_resettle_claim_keeps_one_claim_and_resets_quiet(tmp_path):
    video = str(tmp_path / 'video.flv')
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('initialized')
    journal.append(
        'session_state',
        room_id=123,
        state='waiting',
        session_id=None,
        session_paths=(),
        snapshot={video: (100, 1)},
        quiet_since=None,
        started_at=None,
    )
    append_pending_resettle(journal, video)
    first = BililiveSessionMonitor(
        journal=journal,
        room_id=123,
        id_factory=lambda: 'replacement-session',
    )
    first.observe(at(13), RoomState(False, False), {video: (200, 2)})

    restarted = BililiveSessionMonitor(
        journal=journal,
        room_id=123,
        id_factory=lambda: 'must-not-be-used',
    )
    resumed = restarted.observe(
        at(13, 10), RoomState(False, False), {video: (200, 2)}
    )

    assert resumed.session_id == 'replacement-session'
    assert resumed.state is SessionState.SETTLING
    assert resumed.quiet_since == at(13, 10)
    events = [
        line for line in journal.path.read_text().splitlines()
        if '"event":"session_resettle_started"' in line
    ]
    assert len(events) == 1


def test_pending_resettle_never_overwrites_active_session(tmp_path):
    old_video = str(tmp_path / 'old.flv')
    active_video = str(tmp_path / 'active.flv')
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('initialized')
    journal.append(
        'session_state',
        room_id=123,
        state='recording',
        session_id='active-session',
        session_paths=(active_video,),
        snapshot={active_video: (10, 1)},
        quiet_since=at(12).isoformat(),
        started_at=at(12).isoformat(),
    )
    append_pending_resettle(journal, old_video)
    monitor = BililiveSessionMonitor(
        journal=journal,
        room_id=123,
        id_factory=lambda: 'replacement-session',
    )

    decision = monitor.observe(
        at(13),
        RoomState(True, True),
        {active_video: (20, 2), old_video: (200, 2)},
    )

    assert decision.session_id == 'active-session'
    replay = journal.replay()
    assert replay.session.session_id == 'active-session'
    assert len(replay.pending_resettles) == 1


def test_pending_resettle_without_current_flv_remains_protected(tmp_path):
    video = str(tmp_path / 'video.flv')
    xml = str(tmp_path / 'video.xml')
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('initialized')
    journal.append(
        'session_state',
        room_id=123,
        state='waiting',
        session_id=None,
        session_paths=(),
        snapshot={video: (100, 1)},
        quiet_since=None,
        started_at=None,
    )
    append_pending_resettle(journal, video)
    monitor = BililiveSessionMonitor(
        journal=journal,
        room_id=123,
        id_factory=lambda: 'replacement-session',
    )

    with pytest.raises(ValueError, match='current source FLV'):
        monitor.observe(at(13), RoomState(False, False), {xml: (20, 2)})

    replay = journal.replay()
    assert replay.session.state is SessionState.WAITING
    assert len(replay.pending_resettles) == 1


def test_pending_resettle_discards_durably_deleted_published_source(tmp_path):
    video = str(tmp_path / 'video.flv')
    xml = str(tmp_path / 'video.xml')
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
    append_pending_resettle(journal, video)
    journal.append(
        'file_ready',
        fingerprint='published-source',
        manifest_id='old-session',
        file=video,
        xml_file=xml,
        title='recording',
        start_time=at(8).isoformat(),
        duration=60,
        source_size=100,
        source_mtime_ns=1,
        caption_status='pending',
    )
    journal.append(
        'video_uploaded', fingerprint='published-source', video_id='yt-id'
    )
    journal.append(
        'caption_uploaded',
        fingerprint='published-source',
        caption_status='uploaded',
        caption_track_id='caption-id',
    )
    journal.append('youtube_processed', fingerprint='published-source')
    journal.append(
        'source_deleted',
        fingerprint='published-source', path=video, reason='disk pressure',
    )

    monitor = BililiveSessionMonitor(journal=journal, room_id=123)
    decision = monitor.observe(at(13), RoomState(False, False), {})

    assert decision.state is SessionState.WAITING
    replay = journal.replay()
    assert replay.pending_resettles == ()
    assert replay.manifests[0].invalidated is True
    events = [
        record['event']
        for record in map(json.loads, journal.path.read_text().splitlines())
    ]
    assert events[-1] == 'session_resettle_discarded'


def test_restart_rejects_observation_before_durable_manifest_settlement(
    tmp_path,
):
    video = str(tmp_path / 'a.flv')
    journal = JsonlJournal(tmp_path / 'state.jsonl')
    journal.append('initialized')
    journal.append(
        'session_state',
        room_id=123,
        state='settling',
        session_id='session-1',
        session_paths=(video,),
        snapshot={video: (200, 2)},
        quiet_since=at(22).isoformat(),
        started_at=at(18).isoformat(),
    )
    journal.append(
        'session_manifest_ready',
        manifest_id='session-1',
        room_id=123,
        started_at=at(18).isoformat(),
        settled_at=at(22, 30).isoformat(),
        flv_paths=(video,),
        snapshot={video: (200, 2)},
    )
    restarted = BililiveSessionMonitor(journal=journal, room_id=123)

    with pytest.raises(ValueError, match='earlier'):
        restarted.observe(
            at(22, 20), RoomState(False, False), {video: (200, 2)}
        )


def _replay_with_active_session_and_manifest(
    *,
    state=SessionState.SETTLING,
    initialized=True,
    session_paths=('a.flv', 'a.xml'),
    session_snapshot=None,
    session_started=None,
    quiet_since=None,
    manifest_paths=('a.flv',),
    manifest_snapshot=None,
    manifest_started=None,
    manifest_settled=None,
):
    session_snapshot = session_snapshot or {
        'a.flv': (200, 2),
        'a.xml': (20, 2),
    }
    manifest_snapshot = manifest_snapshot or dict(session_snapshot)
    session_started = session_started or at(18).isoformat()
    quiet_since = quiet_since or at(22).isoformat()
    manifest_started = manifest_started or session_started
    manifest_settled = manifest_settled or at(22, 30).isoformat()
    return JournalReplay(
        files={},
        manifests=(
            JournalManifest(
                manifest_id='session-1',
                room_id=123,
                started_at=manifest_started,
                settled_at=manifest_settled,
                flv_paths=manifest_paths,
                snapshot=manifest_snapshot,
            ),
        ),
        session=JournalSessionState(
            state=state,
            room_id=123,
            session_id='session-1',
            session_paths=session_paths,
            snapshot=session_snapshot,
            quiet_since=quiet_since,
            started_at=session_started,
        ),
        initialized=initialized,
    )


def test_restore_rejects_matching_manifest_id_with_different_flv_paths():
    replay = _replay_with_active_session_and_manifest(
        session_paths=('a.flv', 'b.flv', 'a.xml'),
        session_snapshot={
            'a.flv': (200, 2),
            'b.flv': (300, 3),
            'a.xml': (20, 2),
        },
        manifest_paths=('b.flv',),
    )

    with pytest.raises(ValueError, match='flv_paths'):
        SessionMonitorState.restore(replay)


def test_restore_rejects_matching_manifest_id_with_different_snapshot():
    replay = _replay_with_active_session_and_manifest(
        manifest_snapshot={
            'a.flv': (201, 2),
            'a.xml': (20, 2),
        }
    )

    with pytest.raises(ValueError, match='snapshot'):
        SessionMonitorState.restore(replay)


def test_restore_rejects_matching_manifest_id_with_different_start_time():
    replay = _replay_with_active_session_and_manifest(
        manifest_started=at(18, 1).isoformat()
    )

    with pytest.raises(ValueError, match='started_at'):
        SessionMonitorState.restore(replay)


def test_restore_accepts_matching_manifest_start_time_with_equivalent_offset():
    replay = _replay_with_active_session_and_manifest(
        session_started='2026-07-27T18:00:00+09:00',
        manifest_started='2026-07-27T09:00:00+00:00',
    )

    restored = SessionMonitorState.restore(replay)

    assert restored.state is SessionState.WAITING
    assert restored.session_id is None


def test_restore_rejects_matching_manifest_for_other_room():
    replay = _replay_with_active_session_and_manifest()

    with pytest.raises(ValueError, match='room_id'):
        SessionMonitorState.restore(replay, room_id=456)


def test_restore_compares_manifest_with_minimal_session_snapshot_subset():
    replay = _replay_with_active_session_and_manifest(
        session_snapshot={
            'a.flv': (200, 2),
            'a.xml': (20, 2),
            'historical.flv': (900, 9),
        },
        manifest_snapshot={
            'a.flv': (200, 2),
            'a.xml': (20, 2),
        },
    )

    restored = SessionMonitorState.restore(replay, room_id=123)

    assert restored.state is SessionState.WAITING


@pytest.mark.parametrize(
    ('state', 'initialized'),
    [
        (SessionState.SKIP_CURRENT_SESSION, False),
        (SessionState.RECORDING, True),
    ],
)
def test_restore_rejects_manifest_from_non_settled_active_state(
    state, initialized
):
    replay = _replay_with_active_session_and_manifest(
        state=state, initialized=initialized
    )

    with pytest.raises(ValueError, match='state'):
        SessionMonitorState.restore(replay)


def test_restore_rejects_manifest_settled_before_full_quiet_period():
    replay = _replay_with_active_session_and_manifest(
        manifest_settled=at(22, 29).isoformat()
    )

    with pytest.raises(ValueError, match='quiet period'):
        SessionMonitorState.restore(replay)


@pytest.mark.parametrize('state', [SessionState.SETTLING, SessionState.READY])
def test_restore_accepts_manifest_at_exact_quiet_period_boundary(state):
    replay = _replay_with_active_session_and_manifest(
        state=state,
        quiet_since=at(22).isoformat(),
        manifest_settled=at(22, 30).isoformat(),
    )

    restored = SessionMonitorState.restore(replay)

    assert restored.state is SessionState.WAITING
    assert restored.session_id is None


def test_monitor_decision_snapshot_is_copied_and_read_only():
    source = {'a.flv': (100, 1)}
    decision = armed_machine().observe(
        at(18), RoomState(True, True), source
    )

    source.clear()
    assert decision.snapshot == {'a.flv': (100, 1)}
    with pytest.raises(TypeError):
        decision.snapshot['other.flv'] = (1, 1)


@pytest.mark.parametrize(
    'session',
    [
        JournalSessionState(
            state=SessionState.RECORDING,
            room_id=123,
            session_id=None,
            session_paths=(),
            snapshot={},
            quiet_since=at(18).isoformat(),
            started_at=at(18).isoformat(),
        ),
        JournalSessionState(
            state=SessionState.SETTLING,
            room_id=123,
            session_id='session-1',
            session_paths=('a.flv',),
            snapshot={'a.flv': (100, 1)},
            quiet_since=None,
            started_at=at(18).isoformat(),
        ),
        JournalSessionState(
            state=SessionState.WAITING,
            room_id=123,
            session_id='stale',
            session_paths=('a.flv',),
            snapshot={'a.flv': (100, 1)},
            quiet_since=at(18).isoformat(),
            started_at=at(18).isoformat(),
        ),
    ],
)
def test_restore_rejects_inconsistent_session_state(session):
    replay = JournalReplay(
        files={}, manifests=(), session=session, initialized=True
    )

    with pytest.raises(ValueError, match='session state'):
        SessionMonitorState.restore(replay)


def test_restore_validates_uninitialized_partial_session_before_ignoring_it():
    replay = JournalReplay(
        files={},
        manifests=(),
        session=JournalSessionState(
            state=SessionState.WAITING,
            room_id=123,
            session_id='stale',
            session_paths=('a.flv',),
            snapshot={'a.flv': (100, 1)},
            quiet_since=at(18).isoformat(),
            started_at=at(18).isoformat(),
        ),
        initialized=False,
    )

    with pytest.raises(ValueError, match='session state'):
        SessionMonitorState.restore(replay)


def test_restore_rejects_unsupported_publishing_state():
    replay = JournalReplay(
        files={},
        manifests=(),
        session=JournalSessionState(
            state=SessionState.PUBLISHING,
            room_id=123,
            session_id=None,
            session_paths=(),
            snapshot={},
            quiet_since=None,
            started_at=None,
        ),
        initialized=True,
    )

    with pytest.raises(ValueError, match='unsupported'):
        SessionMonitorState.restore(replay)


def test_observe_rejects_time_earlier_than_persisted_session_time():
    machine = armed_machine()
    machine.observe(at(18), RoomState(True, True), {'a.flv': (100, 1)})

    with pytest.raises(ValueError, match='earlier'):
        machine.observe(
            at(17), RoomState(True, True), {'a.flv': (100, 1)}
        )


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

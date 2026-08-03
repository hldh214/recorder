import threading
import time
from collections import deque
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from recorder.bililive.models import RoomState, SessionState
from recorder.bililive.monitor import MonitorDecision
from recorder.bililive.service import BililiveDirectoryService


NOW = datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc)


def wait_until(predicate, timeout=1):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.005)
    raise AssertionError('condition was not reached before timeout')


class FakeJournal:
    def __init__(self):
        self.replay_calls = 0
        self.events = []
        self._lock = threading.Lock()

    def replay(self):
        with self._lock:
            self.replay_calls += 1
        return SimpleNamespace(files={})

    def append(self, event, **fields):
        with self._lock:
            self.events.append((event, fields))


class FakeMonitor:
    def __init__(self, decisions, journal=None):
        self.decisions = deque(decisions)
        self.calls = []
        self.journal = journal

    def observe(self, now, room, snapshot):
        self.calls.append((now, room, dict(snapshot)))
        decision = self.decisions.popleft()
        if self.journal is not None:
            self.journal.append(
                'session_state',
                state=decision.state.value,
                snapshot=dict(snapshot),
            )
        return decision


class FakeCleanup:
    def __init__(self, events=None):
        self.calls = []
        self.events = events

    def run(self, states, dry_run):
        self.calls.append((tuple(states), dry_run))
        if self.events is not None:
            self.events.append('cleanup')
        return SimpleNamespace(deleted=(), protected=())


class FakeRunner:
    def __init__(self, results=(None,), events=None):
        self.results = deque(results)
        self.calls = 0
        self.events = events

    def run_pending_once(self, replay):
        del replay
        self.calls += 1
        if self.events is not None:
            self.events.append('runner')
        return self.results.popleft() if self.results else None


def decision(state):
    return MonitorDecision(state=state)


def service_for(
    *, room, monitor, journal=None, runner=None, cleanup=None,
    snapshots=None, worker_wait_seconds=3600, worker_join_timeout_seconds=.1,
):
    journal = journal or FakeJournal()
    snapshots = deque(snapshots or ({},))
    return BililiveDirectoryService(
        journal=journal,
        monitor=monitor,
        runner=runner or FakeRunner(),
        cleanup=cleanup or FakeCleanup(),
        room_state_provider=lambda: room,
        snapshot_provider=lambda: snapshots.popleft(),
        clock=lambda: NOW,
        worker_wait_seconds=worker_wait_seconds,
        worker_join_timeout_seconds=worker_join_timeout_seconds,
    )


@pytest.mark.parametrize(
    ('room', 'state'),
    [
        (RoomState(True, False), SessionState.WAITING),
        (RoomState(False, True), SessionState.WAITING),
        (RoomState(False, False), SessionState.RECORDING),
        (RoomState(False, False), SessionState.SETTLING),
    ],
)
def test_available_observation_runs_cleanup_but_blocks_publication(
    room, state
):
    cleanup = FakeCleanup()
    runner = FakeRunner()
    service = service_for(
        room=room,
        monitor=FakeMonitor([decision(state)]),
        cleanup=cleanup,
        runner=runner,
    )

    service.start()
    observed = service.observe_once()
    wait_until(lambda: len(cleanup.calls) == 1)
    service.stop()

    assert observed.state is state
    assert len(cleanup.calls) == 1
    assert runner.calls == 0


def test_unavailable_room_blocks_cleanup_and_publication():
    cleanup = FakeCleanup()
    runner = FakeRunner()
    service = service_for(
        room=None,
        monitor=FakeMonitor([decision(SessionState.WAITING)]),
        cleanup=cleanup,
        runner=runner,
    )

    service.start()
    service.observe_once()
    time.sleep(.03)
    service.stop()

    assert cleanup.calls == []
    assert runner.calls == 0


@pytest.mark.parametrize('state', [SessionState.READY, SessionState.WAITING])
def test_settled_offline_observation_wakes_one_cleanup_then_runner_iteration(state):
    events = []
    cleanup = FakeCleanup(events)
    runner = FakeRunner(events=events)
    service = service_for(
        room=RoomState(False, False),
        monitor=FakeMonitor([decision(state)]),
        cleanup=cleanup,
        runner=runner,
    )

    service.start()
    service.observe_once()
    wait_until(lambda: runner.calls == 1)
    service.stop()

    assert events == ['cleanup', 'runner']
    assert len(cleanup.calls) == 1
    assert runner.calls == 1


def test_retryable_runner_result_waits_for_the_next_worker_wake():
    runner = FakeRunner(results=(SimpleNamespace(status='retryable'), None))
    service = service_for(
        room=RoomState(False, False),
        monitor=FakeMonitor([decision(SessionState.WAITING)]),
        runner=runner,
    )

    service.start()
    service.observe_once()
    wait_until(lambda: runner.calls == 1)
    time.sleep(.03)
    service.stop()

    assert runner.calls == 1


def test_later_active_observation_closes_gate_before_next_item():
    started = threading.Event()
    release = threading.Event()

    class BlockingRunner(FakeRunner):
        def run_pending_once(self, replay):
            del replay
            self.calls += 1
            started.set()
            assert release.wait(1)
            return SimpleNamespace(status='complete')

    runner = BlockingRunner()
    cleanup = FakeCleanup()
    rooms = deque((RoomState(False, False), RoomState(True, False)))
    service = BililiveDirectoryService(
        journal=FakeJournal(),
        monitor=FakeMonitor([
            decision(SessionState.WAITING),
            decision(SessionState.RECORDING),
        ]),
        runner=runner,
        cleanup=cleanup,
        room_state_provider=lambda: rooms.popleft(),
        snapshot_provider=lambda: {},
        clock=lambda: NOW,
        worker_wait_seconds=3600,
        worker_join_timeout_seconds=.1,
    )

    service.start()
    service.observe_once()
    assert started.wait(1)
    service.observe_once()
    release.set()
    wait_until(lambda: len(cleanup.calls) == 2)
    service.stop()

    assert len(cleanup.calls) == 2
    assert runner.calls == 1


def test_gate_closing_during_worker_replay_blocks_next_item():
    replay_started = threading.Event()
    release_replay = threading.Event()

    class BlockingJournal(FakeJournal):
        def __init__(self):
            super().__init__()
            self.block_next = threading.Event()

        def replay(self):
            replay = super().replay()
            if self.block_next.is_set():
                self.block_next.clear()
                replay_started.set()
                assert release_replay.wait(1)
            return replay

    journal = BlockingJournal()

    class BlockingCleanup(FakeCleanup):
        def run(self, states, dry_run):
            result = super().run(states, dry_run)
            journal.block_next.set()
            return result

    runner = FakeRunner()
    rooms = deque((RoomState(False, False), RoomState(True, False)))
    service = BililiveDirectoryService(
        journal=journal,
        monitor=FakeMonitor([
            decision(SessionState.WAITING),
            decision(SessionState.RECORDING),
        ]),
        runner=runner,
        cleanup=BlockingCleanup(),
        room_state_provider=lambda: rooms.popleft(),
        snapshot_provider=lambda: {},
        clock=lambda: NOW,
        worker_wait_seconds=3600,
        worker_join_timeout_seconds=.1,
    )

    service.start()
    service.observe_once()
    assert replay_started.wait(1)
    service.observe_once()
    release_replay.set()
    time.sleep(.03)
    service.stop()

    assert runner.calls == 0


def test_observation_exception_does_not_reuse_previous_open_gate():
    class RaisingMonitor(FakeMonitor):
        def observe(self, now, room, snapshot):
            if self.calls:
                raise RuntimeError('monitor failed')
            return super().observe(now, room, snapshot)

    runner = FakeRunner()
    cleanup = FakeCleanup()
    service = service_for(
        room=RoomState(False, False),
        monitor=RaisingMonitor([decision(SessionState.WAITING)]),
        runner=runner,
        cleanup=cleanup,
        snapshots=({}, {}),
    )

    service.start()
    service.observe_once()
    wait_until(lambda: runner.calls == 1)

    with pytest.raises(RuntimeError, match='monitor failed'):
        service.observe_once()
    service.wake_worker()
    time.sleep(.03)
    service.stop()

    assert len(cleanup.calls) == 1
    assert runner.calls == 1


def test_blocked_publication_does_not_block_main_thread_journal_observations():
    journal = FakeJournal()
    started = threading.Event()
    release = threading.Event()

    class BlockingRunner:
        def __init__(self):
            self.calls = 0
            self.active = 0
            self.max_active = 0

        def run_pending_once(self, replay):
            del replay
            self.calls += 1
            self.active += 1
            self.max_active = max(self.max_active, self.active)
            started.set()
            assert release.wait(1)
            self.active -= 1
            return SimpleNamespace(status='complete')

    runner = BlockingRunner()
    rooms = deque((
        RoomState(False, False),
        RoomState(True, False),
        RoomState(True, False),
    ))
    snapshots = deque((
        {'/room/a.flv': (1, 1)},
        {'/room/a.flv': (2, 2)},
        {'/room/a.flv': (3, 3)},
    ))
    monitor = FakeMonitor([
        decision(SessionState.WAITING),
        decision(SessionState.RECORDING),
        decision(SessionState.RECORDING),
    ], journal=journal)
    service = BililiveDirectoryService(
        journal=journal,
        monitor=monitor,
        runner=runner,
        cleanup=FakeCleanup(),
        room_state_provider=lambda: rooms.popleft(),
        snapshot_provider=lambda: snapshots.popleft(),
        clock=lambda: NOW,
        worker_wait_seconds=3600,
        worker_join_timeout_seconds=.1,
    )

    service.start()
    service.observe_once()
    assert started.wait(1)
    before = time.monotonic()
    service.observe_once()
    service.observe_once()
    assert time.monotonic() - before < .2

    session_states = [fields for event, fields in journal.events if event == 'session_state']
    assert [item['snapshot'] for item in session_states[-2:]] == [
        {'/room/a.flv': (2, 2)},
        {'/room/a.flv': (3, 3)},
    ]

    service.wake_worker()
    release.set()
    time.sleep(.03)
    service.stop()

    assert runner.max_active == 1
    assert runner.calls == 1


def test_stop_joins_cooperative_worker():
    service = service_for(
        room=RoomState(True, False),
        monitor=FakeMonitor([decision(SessionState.RECORDING)]),
    )

    service.start()
    service.observe_once()
    service.stop()

    assert not service.worker_alive


def test_stop_warns_and_returns_after_join_timeout(caplog):
    started = threading.Event()
    release = threading.Event()

    class BlockingRunner:
        def run_pending_once(self, replay):
            del replay
            started.set()
            release.wait(1)
            return None

    service = service_for(
        room=RoomState(False, False),
        monitor=FakeMonitor([decision(SessionState.WAITING)]),
        runner=BlockingRunner(),
        worker_join_timeout_seconds=.01,
    )

    service.start()
    service.observe_once()
    assert started.wait(1)
    before = time.monotonic()
    service.stop()
    elapsed = time.monotonic() - before

    assert elapsed < .2
    assert service.worker_alive
    assert 'did not stop' in caplog.text

    release.set()
    wait_until(lambda: not service.worker_alive)

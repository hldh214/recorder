import logging
import threading
from datetime import datetime, timezone

from recorder.bililive.models import RoomState, SessionState


WORKER_JOIN_TIMEOUT_SECONDS = 30
WORKER_WAIT_SECONDS = 60
_WORKER_PAUSE_STATUSES = frozenset({
    'ambiguous',
    'fatal',
    'resettle_pending',
    'retry_scheduled',
    'retryable',
    'settling',
})


logger = logging.getLogger(__name__)


class BililiveDirectoryService:
    """Coordinate observations on the main thread and publication on one worker."""

    def __init__(
        self,
        *,
        journal,
        monitor,
        runner,
        cleanup,
        room_state_provider,
        snapshot_provider,
        clock=None,
        worker_wait_seconds=WORKER_WAIT_SECONDS,
        worker_join_timeout_seconds=WORKER_JOIN_TIMEOUT_SECONDS,
    ):
        self.journal = journal
        self.monitor = monitor
        self.runner = runner
        self.cleanup = cleanup
        self.room_state_provider = room_state_provider
        self.snapshot_provider = snapshot_provider
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.worker_wait_seconds = worker_wait_seconds
        self.worker_join_timeout_seconds = worker_join_timeout_seconds

        self._gate_lock = threading.Lock()
        self._cleanup_allowed = False
        self._wake = threading.Event()
        self._stop = threading.Event()
        self._worker = None

    @property
    def worker_alive(self):
        worker = self._worker
        return bool(worker is not None and worker.is_alive())

    def start(self):
        if self.worker_alive:
            raise RuntimeError('Bililive publication worker is already running')
        self._stop.clear()
        self._worker = threading.Thread(
            target=self._worker_main,
            name='bililive-directory-publisher',
            daemon=True,
        )
        self._worker.start()
        # Startup is a durable-state replay opportunity even before an observation.
        self._wake.set()

    def stop(self):
        self._stop.set()
        self._wake.set()
        worker = self._worker
        if worker is None:
            return
        worker.join(self.worker_join_timeout_seconds)
        if worker.is_alive():
            logger.warning(
                'Bililive publication worker did not stop within %.3f seconds',
                self.worker_join_timeout_seconds,
            )

    def wake_worker(self):
        self._wake.set()

    def observe_once(self):
        # Every observation must earn a fresh settled-offline decision. Close
        # pessimistically before API, filesystem, or monitor code can fail.
        with self._gate_lock:
            self._cleanup_allowed = False
        room = self._read_room_state()
        try:
            snapshot = self.snapshot_provider()
        except Exception as exception:
            logger.warning('Could not snapshot Bililive directory: %s', exception)
            room = None
            snapshot = {}

        decision = self.monitor.observe(self.clock(), room, snapshot)
        cleanup_allowed = (
            room is not None
            and not room.active
            and decision.state in {SessionState.READY, SessionState.WAITING}
        )
        with self._gate_lock:
            self._cleanup_allowed = cleanup_allowed
        if cleanup_allowed:
            # The monitor append, including a ready manifest, fsyncs before returning.
            self._wake.set()
        return decision

    def _read_room_state(self):
        try:
            room = self.room_state_provider()
        except Exception as exception:
            logger.warning('BililiveRecorder room state unavailable: %s', exception)
            return None
        if room is None:
            return None
        if not isinstance(room, RoomState):
            logger.warning('BililiveRecorder room state is malformed')
            return None
        return room

    def _gate_open(self):
        with self._gate_lock:
            return self._cleanup_allowed

    def _worker_main(self):
        while not self._stop.is_set():
            self._wake.wait(self.worker_wait_seconds)
            self._wake.clear()
            try:
                replay = self.journal.replay()
                if self._stop.is_set() or not self._gate_open():
                    continue

                # Gate again immediately before the only source-mutating operation.
                if not self._gate_open():
                    continue
                self.cleanup.run(tuple(replay.files.values()), dry_run=False)
                if self._stop.is_set() or not self._gate_open():
                    continue

                while not self._stop.is_set() and self._gate_open():
                    replay = self.journal.replay()
                    if self._stop.is_set() or not self._gate_open():
                        break
                    result = self.runner.run_pending_once(replay)
                    if result is None:
                        break
                    if result.status in _WORKER_PAUSE_STATUSES:
                        break
                    # A live observation may close the gate during an upload. The
                    # current upload finishes, but no following item may start.
                    if not self._gate_open():
                        break
            except Exception:
                logger.exception('Bililive publication worker iteration failed')

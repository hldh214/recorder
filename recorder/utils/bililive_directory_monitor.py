import json
import logging
import stat
import time
from datetime import datetime, timezone
from pathlib import Path

import fire
import httpx

import recorder
from recorder.bililive.cleanup import StateAwareCleanup
from recorder.bililive.journal import (
    AlreadyRunningError,
    JsonlJournal,
    ProcessLock,
)
from recorder.bililive.media import classify_session_files, inspect_media
from recorder.bililive.models import RoomState, SessionState
from recorder.bililive.monitor import (
    POLL_INTERVAL_SECONDS,
    BililiveSessionMonitor,
    SessionMonitorState,
)
from recorder.bililive.runner import BililivePublishRunner
from recorder.bililive.service import BililiveDirectoryService
from recorder.danmaku.bilibili.bililive_xml import iter_bililive_danmaku
from recorder.destination.youtube import Youtube, _upload_rate_bytes_per_second
from recorder.publishing.youtube import YoutubePublishService


logger = logging.getLogger(__name__)


def _youtube_upload_while_live(config):
    value = config.get('upload_while_live', False)
    if not isinstance(value, bool):
        raise TypeError('youtube.upload_while_live must be a boolean')
    if value and _upload_rate_bytes_per_second(config) is None:
        raise ValueError(
            'youtube.upload_while_live requires '
            'youtube.upload_rate_mib_per_second'
        )
    return value


def _room_number(value):
    if isinstance(value, bool):
        raise TypeError('room_id must be an integer')
    try:
        room_id = int(value)
    except (TypeError, ValueError) as exception:
        raise TypeError('room_id must be an integer') from exception
    if room_id < 0 or str(room_id) != str(value).strip():
        raise ValueError('room_id must be a non-negative canonical integer')
    return room_id


def _resolve_paths(root, room_id, state_dir):
    source_root = Path(root).expanduser().resolve()
    if not source_root.is_dir():
        raise ValueError(f'BililiveRecorder root is not a directory: {source_root}')
    room_dir = (source_root / str(room_id)).resolve()
    if not room_dir.is_dir():
        raise ValueError(f'BililiveRecorder room directory is missing: {room_dir}')
    resolved_state = (
        Path(state_dir).expanduser().resolve()
        if state_dir is not None
        else (
            Path(recorder.base_path) / 'var' / 'bililive' / str(room_id)
        ).resolve()
    )
    return room_dir, resolved_state


def _snapshot_directory(room_dir):
    snapshot = {}
    for path in sorted(room_dir.iterdir(), key=lambda item: item.name):
        if path.suffix.lower() not in {'.flv', '.xml'} or path.is_symlink():
            continue
        file_stat = path.stat()
        if not stat.S_ISREG(file_stat.st_mode):
            continue
        snapshot[str(path.resolve())] = (
            file_stat.st_size,
            file_stat.st_mtime_ns,
        )
    return snapshot


def _room_from_payload(payload):
    if not isinstance(payload, dict):
        raise ValueError('room API response must be an object')
    recording = payload.get('recording')
    streaming = payload.get('streaming')
    if type(recording) is not bool or type(streaming) is not bool:
        raise ValueError('room API recording and streaming must be booleans')
    return RoomState(recording=recording, streaming=streaming)


def _http_room_provider(client, api_url, room_id):
    endpoint = f'{api_url.rstrip("/")}/api/room/{room_id}'

    def provide():
        response = client.get(endpoint)
        response.raise_for_status()
        return _room_from_payload(response.json())

    return provide


def _safe_room_state(provider):
    try:
        room = provider()
    except Exception as exception:
        logger.warning('BililiveRecorder room state unavailable: %s', exception)
        return None
    if room is None:
        return None
    if not isinstance(room, RoomState):
        logger.warning('BililiveRecorder room state is malformed')
        return None
    return room


def _dry_run_report(replay, decision, cleanup_result=None):
    payload = {
        'initialized': replay.initialized,
        'journal_files': len(replay.files),
        'manifests': len(replay.manifests),
        'state': decision.state.value,
        'reason': decision.reason,
        'baseline_paths': decision.baseline_paths,
        'ready_paths': decision.ready_paths,
    }
    if cleanup_result is not None:
        payload['cleanup'] = {
            'would_delete': tuple(str(path) for path in cleanup_result.deleted),
            'protected': tuple(str(path) for path in cleanup_result.protected),
            'disk_usage_percent': cleanup_result.disk_usage_percent,
        }
    print(json.dumps(payload, ensure_ascii=False, default=list))


def _dry_run_media_report(replay, decision):
    probe_paths = set(decision.ready_paths)
    for manifest in replay.manifests:
        if not manifest.completed and not manifest.invalidated:
            probe_paths.update(manifest.flv_paths)
    if not probe_paths:
        return

    inspected = []
    for path in sorted(probe_paths):
        try:
            inspected.append(inspect_media(path))
        except Exception as exception:
            print(json.dumps({
                'file': path,
                'probe_status': 'retryable_error',
                'message': str(exception),
            }, ensure_ascii=False))
    if not inspected:
        return

    classified = classify_session_files(inspected)
    for media in inspected:
        item = classified[media.fingerprint]
        report = {
            'file': str(media.path),
            'probe_status': item.status,
            'duration': media.duration,
            'has_video': media.has_video,
            'has_audio': media.has_audio,
            'xml_file': str(media.xml_path),
        }
        if media.xml_path.is_file() and media.duration is not None:
            counters = {}
            try:
                messages = sum(1 for _ in iter_bililive_danmaku(
                    media.xml_path,
                    media.start_time,
                    media.duration,
                    counters,
                ))
                report.update(
                    xml_status='ready', xml_messages=messages,
                    xml_dropped=counters,
                )
            except Exception as exception:
                report.update(xml_status='invalid', xml_error=str(exception))
        else:
            report['xml_status'] = 'missing'
        print(json.dumps(report, ensure_ascii=False))


def _run_dry(*, replay, room_id, room_provider, room_dir, cleanup, once):
    machine = SessionMonitorState.restore(replay, room_id=room_id)
    while True:
        room = _safe_room_state(room_provider)
        try:
            snapshot = _snapshot_directory(room_dir)
        except Exception as exception:
            logger.warning('Could not snapshot Bililive directory: %s', exception)
            room = None
            snapshot = {}
        decision = machine.observe(datetime.now(timezone.utc), room, snapshot)
        cleanup_allowed = (
            room is not None
            and not room.active
            and decision.state in {SessionState.READY, SessionState.WAITING}
        )
        cleanup_result = None
        if cleanup_allowed:
            cleanup_result = cleanup.run(tuple(replay.files.values()), dry_run=True)
        _dry_run_report(replay, decision, cleanup_result)
        if cleanup_allowed:
            _dry_run_media_report(replay, decision)
        if once:
            return 0
        time.sleep(POLL_INTERVAL_SECONDS)


def run_monitor(
    root,
    room_id,
    api_url,
    state_dir=None,
    dry_run=False,
    once=False,
    room_state_provider=None,
):
    """Monitor one BililiveRecorder room and publish settled sessions."""
    client = None
    service = None
    try:
        room_id = _room_number(room_id)
        room_dir, state_path = _resolve_paths(root, room_id, state_dir)
        if room_state_provider is None:
            client = httpx.Client(timeout=5)
            room_state_provider = _http_room_provider(client, api_url, room_id)

        with ProcessLock(state_path):
            journal = JsonlJournal(state_path / 'state.jsonl')
            # Replay before constructing YouTube or cleanup. Mid-file corruption
            # therefore fails closed without remote or source-side effects.
            replay = journal.replay()
            cleanup = StateAwareCleanup(journal, room_dir)

            if dry_run:
                return _run_dry(
                    replay=replay,
                    room_id=room_id,
                    room_provider=room_state_provider,
                    room_dir=room_dir,
                    cleanup=cleanup,
                    once=bool(once),
                )

            youtube_config = recorder.config['youtube']
            upload_while_live = _youtube_upload_while_live(youtube_config)
            youtube = Youtube(youtube_config)
            publisher = YoutubePublishService(youtube, recorder.config)
            runner = BililivePublishRunner(
                journal=journal,
                publisher=publisher,
                room_id=room_id,
                state_dir=state_path,
            )
            monitor = BililiveSessionMonitor(journal, room_id)
            service = BililiveDirectoryService(
                journal=journal,
                monitor=monitor,
                runner=runner,
                cleanup=cleanup,
                room_state_provider=room_state_provider,
                snapshot_provider=lambda: _snapshot_directory(room_dir),
                upload_while_live=upload_while_live,
            )
            try:
                service.start()
                while True:
                    service.observe_once()
                    if once:
                        return 0
                    time.sleep(POLL_INTERVAL_SECONDS)
            finally:
                # Keep the process lock until the sole publication worker has
                # stopped, so another monitor cannot overlap a final upload.
                service.stop()
                service = None
    except (
        AlreadyRunningError,
        OSError,
        TypeError,
        ValueError,
        KeyError,
    ) as exception:
        logger.error('Bililive directory monitor could not start: %s', exception)
        return 2
    finally:
        if service is not None:
            service.stop()
        if client is not None:
            client.close()


def retry_ambiguous(state_dir, fingerprint, reason):
    """Resolve one unknown upload outcome so the monitor may upload it again."""
    state_path = Path(state_dir).expanduser().resolve()
    with ProcessLock(state_path):
        journal = JsonlJournal(state_path / 'state.jsonl')
        state = journal.replay().files.get(fingerprint)
        if state is None:
            raise ValueError(f'unknown fingerprint: {fingerprint}')
        if state.video_id is not None:
            raise ValueError('cannot retry a file with a recorded video_id')
        if not state.ambiguous or state.event != 'ambiguous':
            raise ValueError('file is not in an ambiguous upload state')
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError('reason must be a non-empty string')
        journal.append(
            'video_upload_rejected',
            fingerprint=fingerprint,
            stage='video',
            message=reason.strip(),
        )
    return 0


def supersede(state_dir, fingerprint, reason):
    """Mark one unuploaded primary source as replaced by a recovery source."""
    state_path = Path(state_dir).expanduser().resolve()
    with ProcessLock(state_path):
        journal = JsonlJournal(state_path / 'state.jsonl')
        state = journal.replay().files.get(fingerprint)
        if state is None:
            raise ValueError(f'unknown fingerprint: {fingerprint}')
        if state.video_id is not None:
            raise ValueError('cannot supersede a file with a recorded video_id')
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError('reason must be a non-empty string')
        journal.append(
            'superseded',
            fingerprint=fingerprint,
            reason=reason.strip(),
        )
    return 0


if __name__ == '__main__':
    fire.Fire({
        'run': run_monitor,
        'retry-ambiguous': retry_ambiguous,
        'supersede': supersede,
    })

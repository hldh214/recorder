import json
import logging
import math
import time
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import fire

import recorder
from recorder.bililive.journal import JsonlJournal, ProcessLock
from recorder.bililive.media import inspect_media
from recorder.bililive.models import ClassifiedMedia
from recorder.bililive.runner import BililivePublishRunner
from recorder.danmaku.bilibili import bilibili_danmaku_mongo
from recorder.danmaku.bilibili.bililive_xml import BililiveCaptionArtifact
from recorder.destination.youtube import Youtube
from recorder.publishing.youtube import YoutubePublishService


logger = logging.getLogger(__name__)

ROOM_ID = 1829181560
SOURCE_NAME = str(ROOM_ID)
BACKFILL_FILES = (
    '/mnt/ssd-4t/data/bililiverecorder/1829181560/2026-08-03 13:00:21.flv',
    '/mnt/ssd-4t/data/bililiverecorder/1829181560/2026-08-03 16:00:22.flv',
)
STATE_DIR = Path(recorder.base_path) / 'var' / 'bililive-mongo-backfill' / str(ROOM_ID)
POLL_SECONDS = 5 * 60


def _aware_datetime(value):
    if isinstance(value, datetime):
        instant = value
    else:
        normalized = value[:-1] + '+00:00' if value.endswith(('Z', 'z')) else value
        instant = datetime.fromisoformat(normalized)
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError('timestamp must be timezone-aware')
    return instant


def _complete(state, playlist_required):
    return bool(
        state.video_id
        and state.youtube_processed
        and state.caption_uploaded
        and (not playlist_required or state.playlist_inserted)
    )


def _write_caption_source_marker(state_dir, media):
    marker = state_dir / 'caption-sources' / f'{media.fingerprint}.mongo.json'
    payload = json.dumps({
        'room_id': ROOM_ID,
        'start_time': media.start_time.isoformat(),
        'duration': media.duration,
    }, ensure_ascii=True, sort_keys=True) + '\n'
    marker.parent.mkdir(parents=True, exist_ok=True)
    try:
        existing = marker.read_text(encoding='ascii')
    except FileNotFoundError:
        marker.write_text(payload, encoding='ascii')
    else:
        if existing != payload:
            raise ValueError(f'caption source marker changed: {marker}')
    return marker.resolve()


def _mongo_caption_provider(_marker_path, output_path, start, duration):
    try:
        duration_seconds = float(duration)
        if not math.isfinite(duration_seconds) or duration_seconds < 0:
            raise ValueError('duration must be finite and non-negative')
        output_path = Path(output_path)
        partial_path = output_path.with_suffix(output_path.suffix + '.partial')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        partial_path.unlink(missing_ok=True)
        end = _aware_datetime(start) + timedelta(seconds=duration_seconds)
        highlights = (
            bilibili_danmaku_mongo.gen_caption_and_return_highlights(
                ROOM_ID, start, end, partial_path
            )
        )
        partial_path.replace(output_path)
        return BililiveCaptionArtifact(
            path=output_path,
            highlights=highlights,
            status='ready',
            temporary=True,
        )
    except Exception as exception:
        try:
            partial_path.unlink(missing_ok=True)
        except (NameError, OSError):
            pass
        return BililiveCaptionArtifact(
            path=None,
            status='invalid',
            error_message=str(exception),
        )


def _classified_source(path, state_dir):
    media = inspect_media(path)
    if media.probe_error is not None or media.duration is None:
        raise ValueError(f'backfill source is not playable: {path}: {media.probe_error}')
    if not media.has_video or not media.has_audio:
        raise ValueError(f'backfill source lacks audio or video: {path}')
    marker = _write_caption_source_marker(state_dir, media)
    return ClassifiedMedia(
        media=replace(media, xml_path=marker),
        status='ready',
        reason='operator-selected Mongo backfill source',
        is_tail=True,
    )


def _ensure_ready(journal, classified):
    media = classified.media
    state = journal.replay().files.get(media.fingerprint)
    if state is not None:
        if state.file != str(media.path) or state.xml_file != str(media.xml_path):
            raise ValueError(f'journal source identity conflict: {media.path}')
        return state
    journal.append(
        'file_ready',
        fingerprint=media.fingerprint,
        manifest_id=None,
        file=str(media.path),
        xml_file=str(media.xml_path),
        title=media.stream_title,
        stream_title=media.stream_title,
        start_time=media.start_time.isoformat(),
        duration=media.duration,
        source_size=media.size,
        source_mtime_ns=media.mtime_ns,
        caption_status='pending',
    )
    return journal.replay().files[media.fingerprint]


def _run_due_once(journal, runner, classified_sources, playlist_required):
    now = datetime.now(timezone.utc)
    pending = False
    for classified in classified_sources:
        state = _ensure_ready(journal, classified)
        if _complete(state, playlist_required):
            continue
        pending = True
        if state.event in ('fatal', 'ambiguous') or state.ambiguous:
            logger.error(
                'Backfill requires manual reconciliation for %s: %s',
                state.file,
                state.error_message,
            )
            continue
        if state.retry_at and _aware_datetime(state.retry_at) > now:
            continue
        result = runner.publish_one(
            classified,
            caption_provider=_mongo_caption_provider,
        )
        logger.info(
            'Backfill result: file=%s status=%s video_id=%s message=%s',
            classified.media.path,
            result.status,
            journal.replay().files[classified.media.fingerprint].video_id,
            result.message,
        )
        return False
    return not pending


def run(once=False):
    """Upload the fixed recovery set without copying, moving, or deleting FLVs."""
    state_dir = STATE_DIR.resolve()
    with ProcessLock(state_dir):
        journal = JsonlJournal(state_dir / 'state.jsonl')
        sources = tuple(
            _classified_source(Path(path).resolve(), state_dir)
            for path in BACKFILL_FILES
        )
        source_config = recorder.config['source'][SOURCE_NAME]
        playlist_required = bool(source_config.get('playlist_id'))
        youtube = Youtube(recorder.config['youtube'])
        runner = BililivePublishRunner(
            journal=journal,
            publisher=YoutubePublishService(youtube, recorder.config),
            room_id=ROOM_ID,
            state_dir=state_dir,
        )
        while True:
            complete = _run_due_once(
                journal, runner, sources, playlist_required
            )
            if complete:
                logger.info('Mongo backfill queue complete')
                return 0
            if once:
                return 0
            time.sleep(POLL_SECONDS)


if __name__ == '__main__':
    fire.Fire({'run': run})

import hashlib
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

from recorder.bililive.models import ClassifiedMedia, MediaInfo
from recorder.bililive.timestamps import (
    TimestampReadRetryableError,
    normalized_tags,
    read_xml_start_time,
    resolve_start_time,
)


MIN_NON_TAIL_SIZE_BYTES = 256 * 1024 * 1024
MIN_TAIL_DURATION_SECONDS = 60
FFPROBE_TIMEOUT_SECONDS = 120

_ERROR_TEXT_LIMIT = 2048


class MediaProbeRetryableError(RuntimeError):
    pass


def _bounded_text(value):
    if isinstance(value, bytes):
        value = value.decode('utf-8', errors='replace')
    return str(value or '').strip()[:_ERROR_TEXT_LIMIT]


def _fingerprint(path, stat_result, start_time, valid_duration):
    duration_token = (
        f'{valid_duration:.3f}' if valid_duration is not None else 'invalid'
    )
    payload = '\0'.join(
        (
            str(path),
            str(stat_result.st_size),
            str(stat_result.st_mtime_ns),
            start_time.isoformat(),
            duration_token,
        )
    )
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def _probe_error_from_payload(payload):
    try:
        decoded = json.loads(payload)
    except (TypeError, UnicodeDecodeError, json.JSONDecodeError) as exception:
        return {}, f'invalid ffprobe JSON: {exception}'
    if not isinstance(decoded, dict):
        return {}, 'invalid ffprobe JSON: top-level value is not an object'
    return decoded, None


def _parse_duration(format_info):
    raw_duration = format_info.get('duration')
    if raw_duration is None:
        return None, 'missing media duration'
    if isinstance(raw_duration, bool):
        return None, f'invalid media duration: {raw_duration!r}'
    try:
        duration = float(raw_duration)
    except (TypeError, ValueError):
        return None, f'invalid media duration: {raw_duration!r}'
    if not math.isfinite(duration) or duration < 0:
        return None, f'invalid media duration: {raw_duration!r}'
    return duration, None


def _missing_stream_error(has_video, has_audio):
    if not has_video and not has_audio:
        return 'missing video and audio streams'
    if not has_video:
        return 'missing video stream'
    if not has_audio:
        return 'missing audio stream'
    return None


def _stat(path):
    try:
        return path.stat()
    except OSError as exception:
        raise MediaProbeRetryableError(
            f'could not stat media file {path}: {exception}'
        ) from exception


def inspect_media(
    path,
    ffprobe_path='ffprobe',
    runner=subprocess.run,
    xml_start_reader=read_xml_start_time,
):
    try:
        path = Path(path).resolve()
    except OSError as exception:
        raise MediaProbeRetryableError(
            f'could not resolve media file {path}: {exception}'
        ) from exception
    before = _stat(path)
    args = [
        ffprobe_path,
        '-v',
        'error',
        '-print_format',
        'json',
        '-show_format',
        '-show_streams',
        str(path),
    ]
    if sys.platform.startswith('linux') and shutil.which('ionice'):
        args = ['ionice', '-c3', 'nice', '-n', '10', *args]

    probe_result = None
    probe_error = None
    try:
        probe_result = runner(
            args,
            timeout=FFPROBE_TIMEOUT_SECONDS,
            check=True,
            capture_output=True,
        )
    except subprocess.TimeoutExpired as exception:
        raise MediaProbeRetryableError(
            f'ffprobe timed out after {FFPROBE_TIMEOUT_SECONDS} seconds'
        ) from exception
    except OSError as exception:
        raise MediaProbeRetryableError(
            f'could not run ffprobe for {path}: {exception}'
        ) from exception
    except subprocess.CalledProcessError as exception:
        detail = _bounded_text(exception.stderr)
        suffix = f': {detail}' if detail else ''
        probe_error = (
            f'ffprobe exited with status {exception.returncode}{suffix}'
        )

    after = _stat(path)
    if (before.st_size, before.st_mtime_ns) != (
        after.st_size,
        after.st_mtime_ns,
    ):
        raise MediaProbeRetryableError(f'media file changed during probe: {path}')

    payload = {}
    if probe_result is not None:
        payload, probe_error = _probe_error_from_payload(probe_result.stdout)

    format_info = payload.get('format') or {}
    if not isinstance(format_info, dict):
        format_info = {}
        probe_error = probe_error or 'invalid ffprobe format object'
    tags = format_info.get('tags') or {}
    if not isinstance(tags, dict):
        tags = {}

    try:
        xml_raw_start = xml_start_reader(path.with_suffix('.xml'))
    except TimestampReadRetryableError as exception:
        raise MediaProbeRetryableError(
            f'could not read XML start time for {path}: {exception}'
        ) from exception
    resolution = resolve_start_time(
        path, tags, xml_raw_start, before.st_mtime_ns
    )
    start_time = resolution.start_time
    probe_error = probe_error or resolution.error

    metadata = normalized_tags(tags)
    stream_title = metadata.get('streamtitle')
    if not isinstance(stream_title, str) or not stream_title.strip():
        stream_title = metadata.get('title')
    if not isinstance(stream_title, str) or not stream_title.strip():
        stream_title = None
    else:
        stream_title = stream_title.strip()

    duration, duration_error = _parse_duration(format_info)
    streams = payload.get('streams') or []
    if not isinstance(streams, list):
        streams = []
    has_video = any(
        isinstance(stream, dict) and stream.get('codec_type') == 'video'
        for stream in streams
    )
    has_audio = any(
        isinstance(stream, dict) and stream.get('codec_type') == 'audio'
        for stream in streams
    )
    stream_error = _missing_stream_error(has_video, has_audio)
    probe_error = probe_error or duration_error or stream_error
    valid_duration = duration if probe_error is None else None

    return MediaInfo(
        path=path,
        xml_path=path.with_suffix('.xml'),
        size=before.st_size,
        mtime_ns=before.st_mtime_ns,
        start_time=start_time,
        stream_title=stream_title,
        duration=duration,
        has_video=has_video,
        has_audio=has_audio,
        fingerprint=_fingerprint(path, before, start_time, valid_duration),
        probe_error=probe_error,
    )


def _reason(media, decision):
    return (
        f'{decision}; size={media.size}; duration={media.duration}; '
        f'has_video={media.has_video}; has_audio={media.has_audio}; '
        f'probe_error={media.probe_error!r}'
    )


def classify_session_files(media_files):
    media_files = tuple(media_files)
    fingerprints = set()
    for media in media_files:
        if media.fingerprint in fingerprints:
            raise ValueError(
                f'duplicate media fingerprint: {media.fingerprint}'
            )
        fingerprints.add(media.fingerprint)
    playable = sorted(
        (
            media
            for media in media_files
            if media.probe_error is None
            and media.duration is not None
            and media.has_video
            and media.has_audio
        ),
        key=lambda media: (media.start_time, media.path.name),
    )
    tail_fingerprint = playable[-1].fingerprint if playable else None
    classified = {}
    for media in media_files:
        is_playable = (
            media.probe_error is None
            and media.duration is not None
            and media.has_video
            and media.has_audio
        )
        is_tail = is_playable and media.fingerprint == tail_fingerprint
        if not is_playable:
            status = 'ignored_invalid'
        elif not is_tail and media.size < MIN_NON_TAIL_SIZE_BYTES:
            status = 'ignored_tiny'
        elif is_tail and media.duration < MIN_TAIL_DURATION_SECONDS:
            status = 'ignored_invalid_tail'
        else:
            status = 'ready'
        classified[media.fingerprint] = ClassifiedMedia(
            media=media,
            status=status,
            reason=_reason(media, status),
            is_tail=is_tail,
        )
    return classified

import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

import recorder.bililive.media as media_module
from recorder.bililive.media import (
    FFPROBE_TIMEOUT_SECONDS,
    MIN_NON_TAIL_SIZE_BYTES,
    MediaProbeRetryableError,
    classify_session_files,
    inspect_media,
)
from recorder.bililive.models import MediaInfo
from recorder.bililive.timestamps import TimestampReadRetryableError


SHANGHAI = ZoneInfo('Asia/Shanghai')


def _probe_result(
    *,
    duration='3600.1254',
    streams=({'codec_type': 'video'}, {'codec_type': 'audio'}),
    tags=None,
):
    format_info = {'tags': tags or {}}
    if duration is not None:
        format_info['duration'] = duration
    return SimpleNamespace(
        stdout=json.dumps(
            {'format': format_info, 'streams': list(streams)}
        ).encode(),
        stderr=b'',
    )


def _media_info(
    path,
    *,
    size,
    start,
    duration,
    has_video=True,
    has_audio=True,
    probe_error=None,
):
    path = Path(path)
    return MediaInfo(
        path=path,
        xml_path=path.with_suffix('.xml'),
        size=size,
        mtime_ns=1,
        start_time=datetime.fromtimestamp(start, SHANGHAI),
        stream_title=None,
        duration=duration,
        has_video=has_video,
        has_audio=has_audio,
        fingerprint=f'fp:{path.name}',
        probe_error=probe_error,
    )


def test_inspect_media_uses_bililive_metadata_and_one_low_priority_probe(
    tmp_path, monkeypatch
):
    path = tmp_path / '2026-07-27 19_30_00.flv'
    path.write_bytes(b'video')
    calls = []

    def runner(args, **kwargs):
        calls.append((args, kwargs))
        return _probe_result(
            tags={
                'StartTime': 'Mon, 27 Jul 2026 19:30:00 +0800',
                'title': 'night stream',
            }
        )

    monkeypatch.setattr(media_module.shutil, 'which', lambda name: '/bin/ionice')

    inspected = inspect_media(path, ffprobe_path='/opt/ffprobe', runner=runner)

    assert len(calls) == 1
    assert calls[0] == (
        [
            'ionice',
            '-c3',
            'nice',
            '-n',
            '10',
            '/opt/ffprobe',
            '-v',
            'error',
            '-print_format',
            'json',
            '-show_format',
            '-show_streams',
            str(path.resolve()),
        ],
        {
            'timeout': FFPROBE_TIMEOUT_SECONDS,
            'check': True,
            'capture_output': True,
        },
    )
    assert inspected.start_time == datetime(
        2026, 7, 27, 19, 30, tzinfo=SHANGHAI
    )
    assert inspected.stream_title == 'night stream'
    assert inspected.duration == pytest.approx(3600.1254)
    assert inspected.has_video is True
    assert inspected.has_audio is True
    fingerprint_source = '\0'.join(
        (
            str(path.resolve()),
            str(path.stat().st_size),
            str(path.stat().st_mtime_ns),
            inspected.start_time.isoformat(),
            '3600.125',
        )
    )
    assert inspected.fingerprint == hashlib.sha256(
        fingerprint_source.encode('utf-8')
    ).hexdigest()


def test_inspect_media_falls_back_to_shanghai_filename_timestamp(
    tmp_path, monkeypatch
):
    path = tmp_path / '2026-07-27 19:31:02.flv'
    path.touch()
    monkeypatch.setattr(media_module.shutil, 'which', lambda name: None)

    inspected = inspect_media(path, runner=lambda *args, **kwargs: _probe_result())

    assert inspected.start_time == datetime(
        2026, 7, 27, 19, 31, 2, tzinfo=SHANGHAI
    )


def test_inspect_media_reconciles_real_ffprobe_and_xml_metadata(tmp_path):
    path = tmp_path / 'wrong-name.flv'
    path.write_bytes(b'video')
    path.with_suffix('.xml').write_text(
        '<i><BililiveRecorderRecordInfo '
        'start_time="2026-07-27T20:31:59.1494083+09:00"/></i>',
        encoding='utf8',
    )
    result = _probe_result(tags={
        'StartTime': '2026-07-27T11:31:59.154000Z',
        'Title': 'fallback title',
        'StreamTitle': '56冠神抽',
    })

    inspected = inspect_media(path, runner=lambda *args, **kwargs: result)

    assert inspected.start_time.isoformat() == (
        '2026-07-27T19:31:59.154000+08:00'
    )
    assert inspected.stream_title == '56冠神抽'
    assert inspected.probe_error is None


def test_inspect_media_rejects_ffprobe_xml_timestamp_conflict(tmp_path):
    path = tmp_path / '2026-07-27 19:31:59.flv'
    path.write_bytes(b'video')
    path.with_suffix('.xml').write_text(
        '<i><BililiveRecorderRecordInfo '
        'start_time="2026-07-27T20:32:10+09:00"/></i>',
        encoding='utf8',
    )

    inspected = inspect_media(
        path,
        runner=lambda *args, **kwargs: _probe_result(
            tags={'StartTime': '2026-07-27T11:31:59Z'}
        ),
    )

    assert 'conflicting start times' in inspected.probe_error
    assert classify_session_files([inspected])[inspected.fingerprint].status == (
        'ignored_invalid'
    )


def test_inspect_media_uses_xml_when_ffprobe_start_tag_is_missing(tmp_path):
    path = tmp_path / 'unknown.flv'
    path.write_bytes(b'video')
    path.with_suffix('.xml').write_text(
        '<i><BililiveRecorderRecordInfo '
        'start_time="2026-07-27T20:31:59+09:00"/></i>',
        encoding='utf8',
    )

    inspected = inspect_media(
        path, runner=lambda *args, **kwargs: _probe_result(tags={})
    )

    assert inspected.start_time.isoformat() == '2026-07-27T19:31:59+08:00'
    assert inspected.probe_error is None


def test_malformed_xml_header_does_not_override_valid_ffprobe_time(tmp_path):
    path = tmp_path / 'unknown.flv'
    path.write_bytes(b'video')
    path.with_suffix('.xml').write_text('<i><broken', encoding='utf8')

    inspected = inspect_media(
        path,
        runner=lambda *args, **kwargs: _probe_result(
            tags={'StartTime': '2026-07-27T11:31:59Z'}
        ),
    )

    assert inspected.start_time.isoformat() == '2026-07-27T19:31:59+08:00'
    assert inspected.probe_error is None


def test_inspect_media_retries_when_xml_changes(tmp_path):
    path = tmp_path / '2026-07-27 19:31:59.flv'
    path.write_bytes(b'video')

    def changed_xml(xml_path):
        raise TimestampReadRetryableError(f'changed: {xml_path}')

    with pytest.raises(MediaProbeRetryableError, match='changed'):
        inspect_media(
            path,
            runner=lambda *args, **kwargs: _probe_result(),
            xml_start_reader=changed_xml,
        )


@pytest.mark.parametrize(
    'exception',
    [
        subprocess.TimeoutExpired(['ffprobe'], 120),
        OSError('storage unavailable'),
    ],
)
def test_inspect_media_treats_probe_timeout_and_oserror_as_retryable(
    tmp_path, exception
):
    path = tmp_path / '2026-07-27 19:31:02.flv'
    path.touch()

    def runner(*args, **kwargs):
        raise exception

    with pytest.raises(MediaProbeRetryableError):
        inspect_media(path, runner=runner)


def test_inspect_media_records_stable_probe_failure_with_bounded_stderr(
    tmp_path,
):
    path = tmp_path / '2026-07-27 19:31:02.flv'
    path.touch()
    stderr = b'x' * 10_000

    def runner(*args, **kwargs):
        raise subprocess.CalledProcessError(
            returncode=7, cmd=['ffprobe'], stderr=stderr
        )

    inspected = inspect_media(path, runner=runner)

    assert inspected.duration is None
    assert inspected.has_video is False
    assert inspected.has_audio is False
    assert inspected.probe_error.startswith('ffprobe exited with status 7: ')
    assert len(inspected.probe_error) < len(stderr)
    fingerprint_source = '\0'.join(
        (
            str(path.resolve()),
            str(path.stat().st_size),
            str(path.stat().st_mtime_ns),
            inspected.start_time.isoformat(),
            'invalid',
        )
    )
    assert inspected.fingerprint == hashlib.sha256(
        fingerprint_source.encode('utf-8')
    ).hexdigest()


@pytest.mark.parametrize(
    ('result', 'error_fragment'),
    [
        (SimpleNamespace(stdout=b'{bad json', stderr=b''), 'invalid ffprobe JSON'),
        (_probe_result(duration=None), 'missing media duration'),
        (
            _probe_result(streams=({'codec_type': 'audio'},)),
            'missing video stream',
        ),
        (
            _probe_result(streams=({'codec_type': 'video'},)),
            'missing audio stream',
        ),
    ],
)
def test_inspect_media_records_stable_invalid_results(
    tmp_path, result, error_fragment
):
    path = tmp_path / '2026-07-27 19:31:02.flv'
    path.touch()

    inspected = inspect_media(path, runner=lambda *args, **kwargs: result)

    assert inspected.probe_error is not None
    assert error_fragment in inspected.probe_error
    assert inspected.duration is None or error_fragment.startswith('missing ')


def test_inspect_media_rejects_boolean_duration(tmp_path):
    path = tmp_path / '2026-07-27 19:31:02.flv'
    path.touch()

    inspected = inspect_media(
        path, runner=lambda *args, **kwargs: _probe_result(duration=True)
    )

    assert inspected.duration is None
    assert inspected.probe_error == 'invalid media duration: True'


@pytest.mark.parametrize('duration', [float('nan'), float('inf'), -1])
def test_inspect_media_rejects_non_finite_or_negative_duration(
    tmp_path, duration
):
    path = tmp_path / '2026-07-27 19:31:02.flv'
    path.touch()

    inspected = inspect_media(
        path, runner=lambda *args, **kwargs: _probe_result(duration=duration)
    )

    assert inspected.duration is None
    assert inspected.probe_error.startswith('invalid media duration:')


@pytest.mark.parametrize('fail_probe', [False, True])
def test_inspect_media_retries_when_file_changes_during_probe(
    tmp_path, fail_probe
):
    path = tmp_path / '2026-07-27 19:31:02.flv'
    path.touch()

    def runner(*args, **kwargs):
        path.write_bytes(b'new bytes')
        if fail_probe:
            raise subprocess.CalledProcessError(1, ['ffprobe'], stderr=b'bad')
        return _probe_result()

    with pytest.raises(MediaProbeRetryableError, match='changed during probe'):
        inspect_media(path, runner=runner)


def test_classify_files_ignores_small_non_tail_but_keeps_valid_tail(tmp_path):
    first = _media_info(
        tmp_path / 'a.flv', size=255 * 1024 * 1024, start=1, duration=300
    )
    middle = _media_info(
        tmp_path / 'b.flv', size=2 * 1024**3, start=2, duration=4 * 3600
    )
    tail = _media_info(
        tmp_path / 'c.flv', size=10 * 1024 * 1024, start=3, duration=120
    )

    classified = classify_session_files([first, middle, tail])

    assert classified[first.fingerprint].status == 'ignored_tiny'
    assert classified[middle.fingerprint].status == 'ready'
    assert classified[tail.fingerprint].status == 'ready'
    assert classified[tail.fingerprint].is_tail is True


def test_classify_files_ignores_tail_shorter_than_sixty_seconds(tmp_path):
    tail = _media_info(
        tmp_path / 'tail.flv', size=10 * 1024 * 1024, start=3, duration=59.9
    )

    classified = classify_session_files([tail])

    assert classified[tail.fingerprint].status == 'ignored_invalid_tail'


def test_classify_excludes_trailing_corrupt_file_before_selecting_tail(tmp_path):
    playable = _media_info(
        tmp_path / 'playable.flv', size=10, start=1, duration=120
    )
    corrupt = _media_info(
        tmp_path / 'corrupt.flv',
        size=10,
        start=2,
        duration=None,
        has_video=False,
        has_audio=False,
        probe_error='invalid ffprobe JSON',
    )

    classified = classify_session_files([playable, corrupt])

    assert classified[playable.fingerprint].is_tail is True
    assert classified[playable.fingerprint].status == 'ready'
    assert classified[corrupt.fingerprint].is_tail is False
    assert classified[corrupt.fingerprint].status == 'ignored_invalid'


def test_classification_uses_measured_values_not_expected_cut_duration(tmp_path):
    three_hours = _media_info(
        tmp_path / 'three.flv',
        size=MIN_NON_TAIL_SIZE_BYTES,
        start=1,
        duration=3 * 3600,
    )
    four_hours = _media_info(
        tmp_path / 'four.flv',
        size=MIN_NON_TAIL_SIZE_BYTES,
        start=2,
        duration=4 * 3600,
    )

    classified = classify_session_files([three_hours, four_hours])

    assert classified[three_hours.fingerprint].status == 'ready'
    assert classified[four_hours.fingerprint].status == 'ready'
    for result in classified.values():
        assert f'size={result.media.size}' in result.reason
        assert f'duration={result.media.duration}' in result.reason


def test_classification_rejects_duplicate_fingerprints_before_tail_selection(
    tmp_path,
):
    first = _media_info(
        tmp_path / 'first.flv', size=10, start=1, duration=120
    )
    duplicate = MediaInfo(
        path=tmp_path / 'different.flv',
        xml_path=tmp_path / 'different.xml',
        size=MIN_NON_TAIL_SIZE_BYTES,
        mtime_ns=2,
        start_time=datetime.fromtimestamp(2, SHANGHAI),
        stream_title=None,
        duration=180,
        has_video=True,
        has_audio=True,
        fingerprint=first.fingerprint,
    )

    with pytest.raises(ValueError, match='duplicate media fingerprint'):
        classify_session_files([first, duplicate])

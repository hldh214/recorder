from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from recorder.bililive.timestamps import (
    TIMESTAMP_CONFLICT_TOLERANCE_SECONDS,
    TimestampReadRetryableError,
    read_xml_start_time,
    resolve_start_time,
)


SHANGHAI = ZoneInfo('Asia/Shanghai')


def test_real_metadata_instants_agree_and_return_shanghai_time():
    result = resolve_start_time(
        Path('2026-07-27 19:31:59.flv'),
        {'StartTime': '2026-07-27T11:31:59.154000Z'},
        '2026-07-27T20:31:59.1494083+09:00',
        0,
    )

    assert result.start_time == datetime(
        2026, 7, 27, 19, 31, 59, 154000, tzinfo=SHANGHAI
    )
    assert result.source == 'ffprobe'
    assert result.error is None


@pytest.mark.parametrize('delta', [5, 5.001])
def test_metadata_conflict_boundary(delta):
    result = resolve_start_time(
        Path('ignored.flv'),
        {'starttime': '2026-07-27T11:31:00Z'},
        f'2026-07-27T11:31:{delta:06.3f}Z',
        0,
    )

    if delta <= TIMESTAMP_CONFLICT_TOLERANCE_SECONDS:
        assert result.error is None
    else:
        assert 'conflicting start times' in result.error
        assert 'ffprobe=' in result.error
        assert 'xml=' in result.error


@pytest.mark.parametrize(
    ('filename', 'expected'),
    [
        ('2026-07-27 19:31:59.flv', (2026, 7, 27, 19, 31, 59)),
        ('2026-07-27T19-31-59.flv', (2026, 7, 27, 19, 31, 59)),
        ('2026-07-27_19-31-59.flv', (2026, 7, 27, 19, 31, 59)),
    ],
)
def test_filename_variants_are_explicitly_shanghai(filename, expected):
    result = resolve_start_time(Path(filename), {}, None, 0)

    assert result.start_time == datetime(*expected, tzinfo=SHANGHAI)
    assert result.source == 'filename'
    assert result.error is None


def test_ffprobe_only_and_xml_only_are_accepted():
    ffprobe = resolve_start_time(
        Path('unknown.flv'),
        {'STARTTIME': 'Mon, 27 Jul 2026 19:30:00 +0800'},
        None,
        0,
    )
    xml = resolve_start_time(
        Path('unknown.flv'), {}, '2026-07-27T20:30:00+09:00', 0
    )

    assert ffprobe.start_time.isoformat() == '2026-07-27T19:30:00+08:00'
    assert ffprobe.source == 'ffprobe'
    assert xml.start_time.isoformat() == '2026-07-27T19:30:00+08:00'
    assert xml.source == 'xml'


def test_naive_metadata_uses_shanghai_not_process_timezone(monkeypatch):
    monkeypatch.setenv('TZ', 'America/Los_Angeles')
    result = resolve_start_time(
        Path('unknown.flv'), {'StartTime': '2026-07-27T19:30:00'}, None, 0
    )

    assert result.start_time.isoformat() == '2026-07-27T19:30:00+08:00'


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        ('2026-01-15T08:00:00-05:00', '2026-01-15T21:00:00+08:00'),
        ('2026-07-15T08:00:00-04:00', '2026-07-15T20:00:00+08:00'),
    ],
)
def test_dst_season_offsets_normalize_by_absolute_instant(raw, expected):
    result = resolve_start_time(
        Path('unknown.flv'), {'StartTime': raw}, None, 0
    )

    assert result.start_time.isoformat() == expected


def test_no_valid_source_is_not_uploadable():
    result = resolve_start_time(Path('unknown.flv'), {}, None, 1_000_000_000)

    assert result.source == 'mtime_diagnostic'
    assert result.error == 'missing valid ffprobe, XML, and filename start time'


@pytest.mark.parametrize(
    'record_info',
    [
        '<BililiveRecorderRecordInfo',
        '<x:BililiveRecorderRecordInfo xmlns:x="urn:bililive"',
    ],
)
def test_reads_record_info_without_parsing_danmaku_tail(tmp_path, record_info):
    xml = tmp_path / 'recording.xml'
    xml.write_text(
        f'<i>{record_info} '
        'start_time="2026-07-27T20:31:59.1494083+09:00"/>'
        '<d p="bad">unterminated',
        encoding='utf8',
    )

    assert read_xml_start_time(xml) == (
        '2026-07-27T20:31:59.1494083+09:00'
    )


def test_missing_or_malformed_xml_header_returns_none(tmp_path):
    assert read_xml_start_time(tmp_path / 'missing.xml') is None
    malformed = tmp_path / 'malformed.xml'
    malformed.write_text('<i><broken', encoding='utf8')

    assert read_xml_start_time(malformed) is None


def test_xml_identity_change_is_retryable(tmp_path):
    xml = tmp_path / 'recording.xml'
    xml.write_text(
        '<i><BililiveRecorderRecordInfo '
        'start_time="2026-07-27T00:00:00Z"/></i>',
        encoding='utf8',
    )
    real_stat = Path.stat
    calls = 0

    def changing_stat(path):
        nonlocal calls
        result = real_stat(path)
        calls += 1
        if calls == 2:
            return type('ChangedStat', (), {
                'st_size': result.st_size + 1,
                'st_mtime_ns': result.st_mtime_ns,
            })()
        return result

    with pytest.raises(TimestampReadRetryableError, match='changed'):
        read_xml_start_time(xml, statter=changing_stat)

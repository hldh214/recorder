import re
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree
from zoneinfo import ZoneInfo


SESSION_TIMEZONE = ZoneInfo('Asia/Shanghai')
TIMESTAMP_CONFLICT_TOLERANCE_SECONDS = 5
_FILENAME_TIMESTAMP = re.compile(
    r'^(\d{4}-\d{2}-\d{2})[ T_](\d{2})[:-](\d{2})[:-](\d{2})'
)


@dataclass(frozen=True)
class TimestampResolution:
    start_time: datetime
    source: str
    error: str | None = None


class TimestampReadRetryableError(RuntimeError):
    pass


def read_xml_start_time(
    xml_path,
    statter=lambda path: path.stat(),
    parser=ElementTree.iterparse,
):
    xml_path = Path(xml_path)
    try:
        before = statter(xml_path)
    except FileNotFoundError:
        return None
    except OSError as exception:
        raise TimestampReadRetryableError(
            f'could not stat XML timestamp source {xml_path}: {exception}'
        ) from exception

    raw_start = None
    try:
        events = parser(xml_path, events=('start',))
        for _, element in events:
            if element.tag.rsplit('}', 1)[-1] == 'BililiveRecorderRecordInfo':
                value = element.get('start_time')
                raw_start = (
                    value
                    if isinstance(value, str) and value.strip()
                    else None
                )
                break
        del events
    except ElementTree.ParseError:
        raw_start = None
    except OSError as exception:
        raise TimestampReadRetryableError(
            f'could not read XML timestamp source {xml_path}: {exception}'
        ) from exception

    try:
        after = statter(xml_path)
    except OSError as exception:
        raise TimestampReadRetryableError(
            f'could not re-stat XML timestamp source {xml_path}: {exception}'
        ) from exception
    if (before.st_size, before.st_mtime_ns) != (
        after.st_size,
        after.st_mtime_ns,
    ):
        raise TimestampReadRetryableError(
            f'XML timestamp source changed during read: {xml_path}'
        )
    return raw_start


def normalized_tags(tags):
    return {
        str(name).casefold(): value
        for name, value in tags.items()
        if isinstance(name, str)
    }


def _parse_metadata_time(value):
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip()
    normalized = raw[:-1] + '+00:00' if raw.endswith(('Z', 'z')) else raw
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        try:
            parsed = parsedate_to_datetime(raw)
        except (TypeError, ValueError, OverflowError):
            return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        parsed = parsed.replace(tzinfo=SESSION_TIMEZONE)
    return parsed


def _filename_time(path):
    match = _FILENAME_TIMESTAMP.match(path.stem)
    if match is None:
        return None
    try:
        parsed = datetime.strptime(
            f'{match.group(1)} {match.group(2)}:'
            f'{match.group(3)}:{match.group(4)}',
            '%Y-%m-%d %H:%M:%S',
        )
    except ValueError:
        return None
    return parsed.replace(tzinfo=SESSION_TIMEZONE)


def _shanghai(value):
    return value.astimezone(SESSION_TIMEZONE)


def resolve_start_time(path, tags, xml_start_time, mtime_ns):
    tags = normalized_tags(tags)
    ffprobe = _parse_metadata_time(tags.get('starttime'))
    xml = _parse_metadata_time(xml_start_time)
    if ffprobe is not None and xml is not None:
        difference = abs(
            (
                ffprobe.astimezone(timezone.utc)
                - xml.astimezone(timezone.utc)
            ).total_seconds()
        )
        if difference > TIMESTAMP_CONFLICT_TOLERANCE_SECONDS:
            return TimestampResolution(
                _shanghai(ffprobe),
                'conflict',
                'conflicting start times: '
                f'ffprobe={ffprobe.isoformat()}, xml={xml.isoformat()}, '
                f'difference_seconds={difference:.6f}',
            )
        return TimestampResolution(_shanghai(ffprobe), 'ffprobe')
    if ffprobe is not None:
        return TimestampResolution(_shanghai(ffprobe), 'ffprobe')
    if xml is not None:
        return TimestampResolution(_shanghai(xml), 'xml')
    filename = _filename_time(Path(path))
    if filename is not None:
        return TimestampResolution(filename, 'filename')
    diagnostic = datetime.fromtimestamp(
        mtime_ns / 1_000_000_000, SESSION_TIMEZONE
    )
    return TimestampResolution(
        diagnostic,
        'mtime_diagnostic',
        'missing valid ffprobe, XML, and filename start time',
    )

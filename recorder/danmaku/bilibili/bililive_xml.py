import math
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree

from recorder.danmaku import Caption, generate_highlights, parse_datetime


@dataclass(frozen=True)
class BililiveCaptionArtifact:
    path: Path | None
    highlights: str = ''
    status: str = 'ready'
    dropped_out_of_range: int = 0
    error_message: str | None = None
    temporary: bool = True


def _increment(counters, name):
    counters[name] = counters.get(name, 0) + 1


def _local_name(tag):
    return tag.rsplit('}', 1)[-1]


def _parse_duration(duration):
    try:
        duration_seconds = float(duration)
    except (TypeError, ValueError):
        raise ValueError('duration must be finite and non-negative') from None
    if not math.isfinite(duration_seconds) or duration_seconds < 0:
        raise ValueError('duration must be finite and non-negative')
    return duration_seconds


def _paths_alias(source_path, output_path):
    if source_path.resolve() == output_path.resolve():
        return True
    try:
        return source_path.samefile(output_path)
    except FileNotFoundError:
        return False


def iter_bililive_danmaku(xml_path, start, duration, counters):
    start_epoch = parse_datetime(start).timestamp()
    duration_seconds = _parse_duration(duration)

    root = None
    depth = 0
    for event, element in ElementTree.iterparse(
        xml_path, events=('start', 'end')
    ):
        if event == 'start':
            if root is None:
                root = element
            depth += 1
            continue

        try:
            if _local_name(element.tag) != 'd':
                continue

            content = (element.text or '').strip()
            if not content:
                _increment(counters, 'empty_content')
                continue

            raw_parameters = element.get('p')
            if not raw_parameters:
                _increment(counters, 'malformed_parameters')
                continue

            try:
                seconds = float(raw_parameters.split(',', 1)[0])
            except (TypeError, ValueError):
                _increment(counters, 'malformed_parameters')
                continue

            if not math.isfinite(seconds):
                _increment(counters, 'malformed_parameters')
                continue

            if not 0 <= seconds <= duration_seconds:
                _increment(counters, 'dropped_out_of_range')
                continue

            yield {
                'content': content,
                'generation_time': start_epoch + seconds,
            }
        finally:
            element.clear()
            if depth == 2:
                # BililiveRecorder events are flat, direct children of the root.
                root.clear()
            depth -= 1


def _iter_caption_with_eof_flush(danmaku, start, duration):
    """Flush Caption's buffered EOF cue with an invisible final record.

    Caption compares integer timedelta seconds, so one second is the smallest
    flush gap it recognizes and can extend a cue at the duration boundary by 1s.
    """
    yield from danmaku
    yield {
        'content': '',
        'generation_time': (
            parse_datetime(start).timestamp() + _parse_duration(duration) + 1
        ),
    }


def prepare_bililive_xml_caption(xml_path, output_path, start, duration):
    xml_path = Path(xml_path)
    output_path = Path(output_path)
    partial_path = output_path.with_suffix(output_path.suffix + '.partial')

    caption_counters = {}
    committed = False
    partial_owned = False
    try:
        if _paths_alias(xml_path, output_path):
            raise ValueError('output path must not alias source XML')
        if _paths_alias(xml_path, partial_path):
            raise ValueError(
                'temporary output path must not alias source XML'
            )
        partial_owned = True
        if not xml_path.is_file():
            return BililiveCaptionArtifact(path=None, status='missing')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        partial_path.unlink(missing_ok=True)
        duration = _parse_duration(duration)

        caption_danmaku = iter_bililive_danmaku(
            xml_path, start, duration, caption_counters
        )
        Caption(
            _iter_caption_with_eof_flush(caption_danmaku, start, duration),
            parse_datetime(start),
        ).to_vtt(partial_path)

        highlight_counters = {}
        highlights = generate_highlights(
            iter_bililive_danmaku(xml_path, start, duration, highlight_counters),
            start,
        )
        partial_path.replace(output_path)
        committed = True
    except (ElementTree.ParseError, OSError, TypeError, ValueError) as exception:
        return BililiveCaptionArtifact(
            path=None,
            status='invalid',
            dropped_out_of_range=caption_counters.get('dropped_out_of_range', 0),
            error_message=str(exception),
        )
    finally:
        if partial_owned and not committed:
            try:
                partial_path.unlink(missing_ok=True)
            except OSError:
                pass

    return BililiveCaptionArtifact(
        path=output_path,
        highlights=highlights,
        dropped_out_of_range=caption_counters.get('dropped_out_of_range', 0),
    )

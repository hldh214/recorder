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


def iter_bililive_danmaku(xml_path, start, duration, counters):
    start_epoch = parse_datetime(start).timestamp()
    duration_seconds = float(duration)

    for _, element in ElementTree.iterparse(xml_path, events=('end',)):
        try:
            if element.tag != 'd':
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

            if not 0 <= seconds <= duration_seconds:
                _increment(counters, 'dropped_out_of_range')
                continue

            yield {
                'content': content,
                'generation_time': start_epoch + seconds,
            }
        finally:
            element.clear()


def _iter_caption_with_eof_flush(danmaku, start, duration):
    yield from danmaku
    # Caption buffers its final state; its integer-seconds check needs a 1s flush gap.
    yield {
        'content': '',
        'generation_time': parse_datetime(start).timestamp() + float(duration) + 1,
    }


def prepare_bililive_xml_caption(xml_path, output_path, start, duration):
    xml_path = Path(xml_path)
    output_path = Path(output_path)
    partial_path = output_path.with_suffix(output_path.suffix + '.partial')

    if not xml_path.is_file():
        try:
            partial_path.unlink(missing_ok=True)
        except OSError:
            pass
        return BililiveCaptionArtifact(path=None, status='missing')

    caption_counters = {}
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        partial_path.unlink(missing_ok=True)

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
    except (ElementTree.ParseError, OSError, TypeError, ValueError) as exception:
        try:
            partial_path.unlink(missing_ok=True)
        except OSError:
            pass
        return BililiveCaptionArtifact(
            path=None,
            status='invalid',
            dropped_out_of_range=caption_counters.get('dropped_out_of_range', 0),
            error_message=str(exception),
        )

    return BililiveCaptionArtifact(
        path=output_path,
        highlights=highlights,
        dropped_out_of_range=caption_counters.get('dropped_out_of_range', 0),
    )

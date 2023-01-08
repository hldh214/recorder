import datetime
import pathlib

import arrow

from recorder import video_name_sep, TZ_INFO, ARROW_DATETIME_FORMAT, config
from recorder.danmaku.caption import Caption


def parse_datetime(obj):
    return arrow.get(obj if isinstance(obj, datetime.datetime) else arrow.get(obj, ARROW_DATETIME_FORMAT),
                     tzinfo=TZ_INFO)


def get_info_from_path(path):
    abspath = pathlib.Path(path).resolve()
    start = abspath.parts[-1].split('.')[0]

    if video_name_sep in start:
        start = start.split(video_name_sep)[-1]

    source_name = abspath.parts[-2]
    end = arrow.get(abspath.stat().st_mtime).to(TZ_INFO).format(ARROW_DATETIME_FORMAT)
    current_config = config.get('source').get(source_name)

    return current_config, start, end


def generate_highlights(danmaku, start, topn=10, minute_gap=10):
    """
    :param danmaku: raw mongodb result set
    :param start: start time of the video
    :param topn: top n highlights
    :param minute_gap: gap between highlights
    :return:
    """
    fmt = 'HH:mm'

    highlight_map = {}
    for each in danmaku:
        current_time = arrow.get(each['_id'].generation_time)
        ts_seconds = current_time.timestamp() - parse_datetime(start).timestamp()
        time_in_minutes = arrow.get(ts_seconds).format(fmt)

        if time_in_minutes not in highlight_map:
            highlight_map[time_in_minutes] = 1
        else:
            highlight_map[time_in_minutes] += 1

    # sort by value
    highlights = sorted(highlight_map.items(), key=lambda x: x[1], reverse=True)

    # [ [time_in_minute, heat, topN], ... ]
    result = []
    index = 0
    # topN with minute_gap
    while len(result) < topn:
        if not highlights:
            break

        item = highlights.pop(0)
        insertable = True
        for each in result:
            diff = arrow.get(each[0], fmt) - arrow.get(item[0], fmt)
            if abs(diff.total_seconds()) < minute_gap * 60:
                insertable = False

        if insertable:
            index += 1
            result.append([item[0], item[1], index])

    result = sorted(result, key=lambda x: x[0])

    if not result:
        return ''

    return 'Highlights\n00:00 Start\n' + '\n'.join([f'{each[0]}:00 Top{each[2]} ({each[1]}🔥)' for each in result])

import arrow
import cachetools

CAPTION_MINIMAL_INTERVAL = 0.1  # 两条字幕之间间隔不小于 0.1 秒, 为了字幕播放性能
CONTENT_TTL = 4  # 弹幕展示时间 (秒)
CONTENT_MAXSIZE = 7  # 最多一次显示多少条弹幕

VTT_TIME_FORMAT = 'HH:mm:ss.SSS'
VTT_HEADERS = '''\
WEBVTT
Kind: captions
Language: zh-Hans

'''


class Timer:
    """
    custom timer for `TTLCache`
    """

    def __init__(self, ts):
        self.ts = ts

    def timer(self):
        return self.ts


class Caption:
    """
    iterator = [
        {"content": "danmaku_content", "generation_time": "generation_time_from_mongodb_object_id"},
        {"content": "danmaku_content", "generation_time": "generation_time_from_mongodb_object_id"},
        {"content": "danmaku_content", "generation_time": "generation_time_from_mongodb_object_id"},
        ...
    ]
    """

    def __init__(self, iterator, started_at):
        self.iterator = iterator
        self.started_at = started_at

    def to_vtt(self, output_path):
        last_modified_at = self.started_at
        timer = Timer(self.started_at.timestamp())
        ttl_cache = cachetools.TTLCache(maxsize=CONTENT_MAXSIZE, ttl=CONTENT_TTL, timer=timer.timer)
        last_context = {'ts': None, 'contents': []}

        with open(output_path, 'w', encoding='utf8') as fp:
            fp.write(VTT_HEADERS)

            for each in self.iterator:
                content = each['content']
                current_time = arrow.get(each['generation_time'])

                ts_seconds = current_time.timestamp() - self.started_at.timestamp()
                ts = arrow.get(ts_seconds)

                timer.ts = current_time.timestamp()
                cache_key = f'{ts.format(VTT_TIME_FORMAT)}\n{content}'
                ttl_cache[cache_key] = content
                content_list = list(ttl_cache.values())  # 获取当前字幕需要展示的所有弹幕

                if not last_context['contents']:
                    # 第一次循环
                    last_context['ts'] = ts
                    last_context['contents'] = content_list
                    continue

                caption_interval = current_time - last_modified_at
                if caption_interval.seconds < CAPTION_MINIMAL_INTERVAL:
                    # 控制两条字幕之间间隔时间
                    last_context['contents'] = content_list
                    continue

                last_start = last_context['ts']
                last_end = ts if ts.shift(seconds=-CONTENT_TTL) < last_start else last_start.shift(seconds=CONTENT_TTL)

                line = f'{last_start.format(VTT_TIME_FORMAT)} --> {last_end.format(VTT_TIME_FORMAT)}\n'

                for each_content in last_context['contents']:
                    line += f'{each_content}\n'

                line += '\n'
                fp.write(line)

                last_context['ts'] = ts
                last_context['contents'] = content_list
                last_modified_at = current_time

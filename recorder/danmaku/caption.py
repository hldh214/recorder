import arrow
import cachetools

VTT_CAPTION_MINIMAL_INTERVAL = 0.1  # 两条字幕之间间隔不小于 0.1 秒, 为了字幕播放性能
VTT_CONTENT_TTL = 4  # 弹幕展示时间 (秒)
VTT_CONTENT_MAXSIZE = 7  # 最多一次显示多少条弹幕
VTT_TIME_FORMAT = 'HH:mm:ss.SSS'
VTT_HEADERS = '''\
WEBVTT
Kind: captions
Language: zh-Hans

'''

ASS_STYLE_MEDIUM_FONT_WIDTH = 26  # 26 * 2 == 52
ASS_STYLE_MEDIUM_FONT_HEIGHT = 60  # 60 > 52
ASS_VIEWPORT_WIDTH = 1920
ASS_VIEWPORT_HEIGHT = 1080
ASS_CONTENT_TTL = 15
ASS_TRACK_SIZE = 17  # max 17 rows of dialogue at the same time
ASS_TIME_FORMAT = 'H:mm:ss.SS'
ASS_HEADERS = '''\
[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Small,黑体,36,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,1.2,0,5,0,0,0,0
Style: Medium,黑体,52,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,1.2,0,5,0,0,0,0
Style: Large,黑体,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,1.2,0,5,0,0,0,0
Style: Larger,黑体,72,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,1.2,0,5,0,0,0,0
Style: ExtraLarge,黑体,90,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,1.2,0,5,0,0,0,0

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''


# Credit: https://archive.is/byzKl
class Dialogue:
    def __init__(self, content, start_time):
        """
        :param content: danmaku content
        :param start_time: millisecond
        """
        self.content = content
        self.start_time = start_time

        self.end_time = start_time + ASS_CONTENT_TTL * 1000
        self.end_x = -ASS_STYLE_MEDIUM_FONT_WIDTH * len(content)
        self.start_x = ASS_VIEWPORT_WIDTH - self.end_x
        self.velocity = (self.start_x - self.end_x) / ASS_CONTENT_TTL / 1000

        self.y = None

    def compare(self, prev):
        # calculate the tolerance-able distance between two danmaku
        distance = (self.start_time - prev.start_time) * prev.velocity \
                   - len(prev.content) * ASS_STYLE_MEDIUM_FONT_WIDTH * 2

        # case1: collision
        if distance <= 0:
            return False

        # case2: current is slower than the previous
        if self.velocity - prev.velocity <= 0:
            return True

        # case3: if distance and velocity difference are both greater than 0
        # then calculate the time needed to chase and compare it with the longest time to chase.
        chase_time = distance / (self.velocity - prev.velocity)
        max_chase_time = ASS_CONTENT_TTL * 1000 - (self.start_time - prev.start_time)

        if chase_time > max_chase_time:
            return True

        return False

    @property
    def start(self):
        return arrow.get(self.start_time / 1000).format(ASS_TIME_FORMAT)

    @property
    def end(self):
        return arrow.get(self.end_time / 1000).format(ASS_TIME_FORMAT)


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
        ttl_cache = cachetools.TTLCache(maxsize=VTT_CONTENT_MAXSIZE, ttl=VTT_CONTENT_TTL, timer=timer.timer)
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
                if caption_interval.seconds < VTT_CAPTION_MINIMAL_INTERVAL:
                    # 控制两条字幕之间间隔时间
                    last_context['contents'] = content_list
                    continue

                last_start = last_context['ts']
                last_end = ts if ts.shift(seconds=-VTT_CONTENT_TTL) < last_start else last_start.shift(
                    seconds=VTT_CONTENT_TTL)

                line = f'{last_start.format(VTT_TIME_FORMAT)} --> {last_end.format(VTT_TIME_FORMAT)}\n'

                for each_content in last_context['contents']:
                    line += f'{each_content}\n'

                line += '\n'
                fp.write(line)

                last_context['ts'] = ts
                last_context['contents'] = content_list
                last_modified_at = current_time

    def to_ass(self, output_path):
        tracks = [None for _ in range(ASS_TRACK_SIZE)]

        with open(output_path, 'w', encoding='utf8') as fp:
            fp.write(ASS_HEADERS)

            for each in self.iterator:
                content = each['content']
                current_time = arrow.get(each['generation_time'])
                ts_seconds = current_time.timestamp() - self.started_at.timestamp()

                d = Dialogue(content, ts_seconds * 1000)
                i = 0
                while i < len(tracks):
                    # noinspection PyTypeChecker
                    if tracks[i] is None or d.compare(tracks[i]) is True:
                        # noinspection PyTypeChecker
                        tracks[i] = d
                        d.y = (i + 1) * ASS_STYLE_MEDIUM_FONT_HEIGHT
                        break
                    i += 1
                else:
                    print(f'no track for {d.content}, skip it')

                move_content = rf'{{\move({d.start_x},{d.y},{d.end_x},{d.y},0,0)}}' + content

                d = f'Dialogue: 0,{d.start},{d.end},Medium,,0,0,0,,{move_content}'
                fp.write(d + '\n')

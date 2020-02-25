import html
import json
import re

import requests

import recorder.ffmpeg as ffmpeg

stream_pattern = re.compile(r'"stream"\s*:\s*({.+?})\s*};')

opener = requests.session()


def is_live(room_id):
    m3u8_result = parse_m3u8(room_id)

    if m3u8_result and ffmpeg.valid(m3u8_result):
        # on air
        return True

    return False


def parse_m3u8(room_id, sticky_m3u8=None):
    if sticky_m3u8 is not None and sticky_m3u8:
        if ffmpeg.valid(sticky_m3u8):
            return sticky_m3u8

    try:
        res = opener.get('https://www.huya.com/{0}'.format(room_id))
    except requests.exceptions.RequestException:
        return False

    stream_result = stream_pattern.findall(res.text)

    if not stream_result:
        return False

    stream = json.loads(stream_result[0])
    # we choose first source(ali in default)
    stream_info = stream['data'][0]['gameStreamInfoList'][0]
    flv_url = stream_info['sFlvUrl']
    stream_name = stream_info['sStreamName']
    flv_url_suffix = stream_info['sFlvUrlSuffix']
    flv_anti_code = html.unescape(stream_info['sFlvAntiCode'])

    # on air
    return f'{flv_url}/{stream_name}.{flv_url_suffix}?{flv_anti_code}'


if __name__ == '__main__':
    print(is_live('668668'))
    print(parse_m3u8('668668'))

import re

import requests

import recorder.ffmpeg as ffmpeg

hls_url_pattern = re.compile(r'"sHlsUrl"\s*:\s*"(\S+?)"')
stream_name_pattern = re.compile(r'"sStreamName"\s*:\s*"(\S+?)"')
URL_SUFFIX = '.m3u8'

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

    hls_url_result = hls_url_pattern.findall(res.text)
    stream_name_result = stream_name_pattern.findall(res.text)

    if (not hls_url_result) or (not stream_name_result):
        return False

    # on air
    return hls_url_result[0].replace('\\', '') + '/' + stream_name_result[0] + URL_SUFFIX


if __name__ == '__main__':
    print(is_live('668668'))
    print(parse_m3u8('668668'))

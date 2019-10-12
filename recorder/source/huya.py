import re

import requests

import recorder.ffmpeg as ffmpeg

m3u8_pattern = re.compile(r"hasvedio\s*:\s*'(\S+)'")

opener = requests.session()
opener.headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Mobile Safari/537.36'
}


def is_live(room_id):
    try:
        res = opener.get('https://m.huya.com/{0}'.format(room_id))
    except requests.exceptions.ChunkedEncodingError:
        return False
    m3u8_result = m3u8_pattern.findall(res.text)

    if m3u8_result and ffmpeg.valid(m3u8_result[0]):
        # on air
        return True

    return False


def parse_m3u8(room_id, sticky_m3u8=None):
    res = opener.get('https://m.huya.com/{0}'.format(room_id))
    m3u8_result = m3u8_pattern.findall(res.text)

    if not m3u8_result:
        return False

    # on air
    m3u8 = None

    if sticky_m3u8 is not None:
        if opener.get(sticky_m3u8).status_code == 200:
            m3u8 = sticky_m3u8

    if not m3u8:
        # replace sd -> original
        m3u8 = m3u8_result[0].replace('_1200/playlist', '').replace('_1200', '')

    return m3u8


if __name__ == '__main__':
    print(is_live('668668'))
    print(parse_m3u8('668668'))

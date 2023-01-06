import json
import re
import urllib.parse

import requests

from recorder import ffmpeg, logger

render_data_pattern = re.compile(r'<script\s+id="RENDER_DATA"\s+type="application/json">(.+?)</script>')


def get_stream(room_id, **kwargs):
    min_start_time = 0 if kwargs.get('min_start_time') is None else kwargs['min_start_time']

    try:
        res = requests.get(f'https://live.douyin.com/{room_id}', headers={
            'cookie': '__ac_nonce=063b59ce0001243a9217f;',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/108.0.0.0 Safari/537.36'
        })
    except requests.exceptions.RequestException:
        return False

    render_data_result = render_data_pattern.findall(res.text)

    if not render_data_result:
        return False

    render_data = json.loads(urllib.parse.unquote(render_data_result[0]))

    room_data = render_data['app']['initialState']['roomStore']['roomInfo']['room']

    logger.debug(f'[{room_id}]room_data: {json.dumps(room_data)}')

    if 'stream_url' not in room_data:
        return False

    result = room_data['stream_url']['flv_pull_url']['FULL_HD1']

    start_time = ffmpeg.start_time(result)
    if not start_time or start_time < min_start_time:
        return False

    return result


if __name__ == '__main__':
    import time

    while True:
        print(get_stream(590890573))
        print(get_stream(73586090754))
        time.sleep(5)

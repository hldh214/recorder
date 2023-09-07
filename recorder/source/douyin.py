import json

import requests

from recorder import logger

REQUEST_TIMEOUT = 5


def get_room_info(room_id):
    try:
        res = requests.get(
            # Credit: https://github.com/LyzenX/DouyinLiveRecorder/commit/c83a00c8c2d4f4aad25347f3163cd9ced212c99d
            f'https://live.douyin.com/webcast/room/web/enter/?aid=6383&device_platform=web&browser_language=zh-CN'
            f'&browser_platform=Win32&browser_name=Chrome&browser_version=109.0.0.0&web_rid={room_id}',
            headers={
                # todo: make this cookie configurable
                # Credit: https://github.com/ihmily/DouyinLiveRecorder/commit/6018b8f4650f9acd30bea3fca61a66534c9d8184
                'cookie': 'ttwid=1%7CB1qls3GdnZhUov9o2NxOMxxYS2ff6OSvEWbv0ytbES4'
                          '%7C1680522049%7C280d802d6d478e3e78d0c807f7c487e7ffec0ae4e5fdd6a0fe74c3c6af149511',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/108.0.0.0 Safari/537.36',
                'Referer': 'https://live.douyin.com/',
            },
            timeout=REQUEST_TIMEOUT
        )
    except requests.exceptions.RequestException:
        return {}

    try:
        res = res.json()
    except requests.exceptions.JSONDecodeError:
        logger.warning(f'Failed to get room info({room_id}), res: {res.text}')
        return {}

    try:
        return res['data']['data'][0]
    except KeyError:
        logger.warning(f'Failed to get data, res: {res.text}')
        return {}


def get_stream(room_id, **_):
    room_data = get_room_info(room_id)

    if 'stream_url' not in room_data:
        return False

    logger.debug(f'[{room_id}]room_data: {json.dumps(room_data)}')

    try:
        flv_url = room_data['stream_url']['flv_pull_url']['FULL_HD1']
        hls_url = room_data['stream_url']['hls_pull_url_map']['FULL_HD1']
    except KeyError:
        logger.error(f'Failed to get stream url, room_data: {room_data}')
        return False

    return {
        'flv_url': flv_url,
        'hls_url': hls_url,
        'title': room_data.get('title'),
    }


if __name__ == '__main__':
    import time
    import logging

    logger.setLevel(logging.DEBUG)

    while True:
        print(get_stream(590890573))
        time.sleep(5)

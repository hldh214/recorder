import random

import requests

from recorder.ffmpeg import USER_AGENTS
from recorder import logger


def get_stream(room_id, **kwargs):
    sess_key = kwargs.get('sess_key')
    if not sess_key:
        sess_key = kwargs.get('panda').get('sess_key')

    proxies = None
    if 'proxy' in kwargs.get('panda'):
        proxies = {
            'http': kwargs.get('panda').get('proxy'),
            'https': kwargs.get('panda').get('proxy')
        }

    try:
        res = requests.post('https://api.pandalive.co.kr/v1/live/play', data={
            'action': 'watch',
            'userId': room_id,
        }, headers={
            'cookie': f'sessKey={sess_key}',
            'origin': 'https://www.pandalive.co.kr',
            'referer': 'https://www.pandalive.co.kr/',
            'user-agent': random.choice(USER_AGENTS),
            'x-device-info': '{"t":"webPc","v":"1.0","ui":17784756}'
        }, proxies=proxies).json()
    except requests.exceptions.RequestException:
        return False

    logger.debug(f'panda.get_stream: {res}')

    if 'PlayList' not in res:
        return False

    try:
        return {
            'hls_url': res['PlayList']['hls'][0]['url']
        }
    except (TypeError, LookupError) as e:
        logger.warning(f'panda.get_stream with error[{e}]: {res}')
        return False


if __name__ == '__main__':
    import time

    while True:
        print(get_stream('10535725', sess_key='018c6d30a09720dd7aba6a9113fa5227bc9c78e033eb1a2be5fec88af599e3c6'))
        time.sleep(5)

import array
import asyncio
import inspect
import json
import os
import pathlib
import random
import re
import subprocess

import requests
import websockets
import websockets.exceptions

from recorder import logger, ffmpeg

REQUEST_TIMEOUT = 5
WS_API = 'wss://wsapi.huya.com'
PREFERRED_CDN_TYPE = 'AL'
CDN_BLACKLIST = ('TX',)
PREFERRED_FORMAT = 'flv'
NODE_BINARY = 'node'
TAF_COMMAND = NODE_BINARY, os.path.join(pathlib.Path(__file__).parent, 'taf.js')

sub_sid_pattern = re.compile(r'"lUid"\s*:\s*(\d+)')
global_init_pattern = re.compile(r"HNF_GLOBAL_INIT\s*=\s*({.*?})\s*</script>")


def parse_by_mini_program(sub_sid, preferred_cdn_type, preferred_format, ratio, min_start_time):
    try:
        res = requests.get('https://mp.huya.com/cache.php', params={
            'm': 'Live',
            'do': 'profileRoom',
            'pid': sub_sid,
            'showSecret': '1'
        }, headers={
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_3_1 like Mac OS X) AppleWebKit/605.1.15 '
                          '(KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.18(0x18001231) NetType/WIFI '
                          'Language/zh_CN',
            'Referer': 'https://servicewechat.com/wx74767bf0b684f7d3/244/page-frame.html',  # 244?
            'content-type': 'application/json'
        }, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.RequestException:
        return False

    logger.debug(f'parse_by_mini_program({sub_sid}): {res.text}')

    try:
        stream_info = res.json()['data']['stream']['baseSteamInfoList']

        return parse_stream_info(stream_info, preferred_cdn_type, preferred_format, ratio, min_start_time)
    except (LookupError, ValueError, TypeError):
        return False


def parse_by_ws(sub_sid, ws_api, preferred_cdn_type, preferred_format, ratio, min_start_time):
    stream_info = asyncio.run(get_stream_ng(sub_sid, ws_api))

    if not stream_info:
        return False

    return parse_stream_info(stream_info, preferred_cdn_type, preferred_format, ratio, min_start_time)


async def get_stream_ng(sub_sid, ws_api):
    try:
        async with websockets.connect(ws_api, close_timeout=REQUEST_TIMEOUT) as websocket:
            await asyncio.wait_for(websocket.send(
                array.array('B', get_living_info_request(sub_sid)).tobytes()
            ), timeout=REQUEST_TIMEOUT)

            greeting = await asyncio.wait_for(websocket.recv(), timeout=REQUEST_TIMEOUT)
        living_info = get_living_info_response([each for each in greeting])
    except (OSError, ValueError, websockets.exceptions.WebSocketException, asyncio.TimeoutError):
        return False

    logger.debug(f'parse_by_ws({sub_sid}): {json.dumps(living_info)}')

    if not living_info['bIsLiving']:
        return False

    stream_info = living_info['tNotice']['vStreamInfo']['value']

    if not stream_info:
        return False

    return stream_info


def get_living_info_request(sub_sid):
    return json.loads(subprocess.run([
        *TAF_COMMAND, 'GetLivingInfoReq', str(sub_sid)
    ], stdout=subprocess.PIPE).stdout.decode())


def get_living_info_response(binary_array):
    return json.loads(subprocess.run([
        *TAF_COMMAND, 'GetLivingInfoRsp', str(binary_array)
    ], stdout=subprocess.PIPE).stdout.decode())


def get_stream(room_id, **kwargs):
    try:
        res = requests.get('https://m.huya.com/{0}'.format(room_id), headers={
            'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Mobile Safari/537.36'
        }, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.RequestException:
        return False

    sub_sid_result = sub_sid_pattern.findall(res.text)

    if not sub_sid_result:
        return False

    sub_sid = sub_sid_result[0]

    ratio = '' if kwargs.get('ratio') is None else kwargs['ratio']
    min_start_time = 0 if kwargs.get('min_start_time') is None else kwargs['min_start_time']

    ws_api = random.choice(kwargs['ws_apis']) if 'ws_apis' in kwargs else WS_API
    preferred_cdn_type = kwargs['preferred_cdn_type'] if 'preferred_cdn_type' in kwargs else PREFERRED_CDN_TYPE
    preferred_format = kwargs['preferred_format'] if 'preferred_format' in kwargs else PREFERRED_FORMAT

    result = parse_by_mini_program(sub_sid, preferred_cdn_type, preferred_format, ratio, min_start_time)
    if result:
        return result

    result = parse_by_ws(sub_sid, ws_api, preferred_cdn_type, preferred_format, ratio, min_start_time)
    if result:
        return result

    return False


def parse_stream_info(stream_info, preferred_cdn_type, preferred_format, ratio, min_start_time):
    current_stream_info = next(
        (item for item in stream_info if item['sCdnType'] == preferred_cdn_type),
        stream_info[0]
    )

    if current_stream_info['sCdnType'] in CDN_BLACKLIST:
        return ''

    stream_name = current_stream_info['sStreamName']

    if preferred_format == 'hls':
        url = current_stream_info['sHlsUrl']
        url_suffix = current_stream_info['sHlsUrlSuffix']
        anti_code = current_stream_info['sHlsAntiCode']
    elif preferred_format == 'flv':
        url = current_stream_info['sFlvUrl']
        url_suffix = current_stream_info['sFlvUrlSuffix']
        anti_code = current_stream_info['sFlvAntiCode']
    else:
        return ''

    result = f'{url}/{stream_name}.{url_suffix}?{anti_code}&ratio={ratio}'

    start_time = ffmpeg.start_time(result)
    if not start_time or start_time < min_start_time:
        return ''

    logger.info('caller: {0}, start_time: {1}, result: {2}'.format(
        inspect.stack()[1][3], start_time, result
    ))

    return result


def get_replay(video_id):
    res = requests.get('https://liveapi.huya.com/moment/getMomentContent', params={'videoId': video_id}).json()

    definitions = res['data']['moment']['videoInfo']['definitions']

    return sorted(definitions, key=lambda item: item['definition'])[-1]['url']


if __name__ == '__main__':
    # print(get_replay('677885387'))
    # exit()

    import time

    while True:
        print(get_stream('chonglangtv', ratio='8000'))
        time.sleep(5)

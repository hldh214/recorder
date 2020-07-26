import array
import asyncio
import html
import json
import os
import pathlib
import random
import re
import subprocess

import requests
import websockets

WS_API = 'wss://wsapi.huya.com'
PREFERRED_CDN_TYPE = 'AL'
DISABLED_CDN_TYPE = 'TX'
NODE_BINARY = 'node'
TAF_COMMAND = NODE_BINARY, os.path.join(pathlib.Path(__file__).parent, 'taf.js')

sub_sid_pattern = re.compile(r"ayyuid:\s*'(\d+)'")
m3u8_pattern = re.compile(r"hasvedio\s*:\s*'(\S+)'")


def parse_by_mini_program(sub_sid, preferred_cdn_type):
    try:
        res = requests.get('https://mp.huya.com/cache.php', params={
            'm': 'Live',
            'do': 'profileRoom',
            'pid': sub_sid,
            'showSecret': '1'
        }, headers={
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; ALP-AL00 Build/V417IR; wv) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.100 Mobile Safari/537.36 '
                          'MicroMessenger/7.0.10.1580(0x27000A59) Process/appbrand0 '
                          'NetType/WIFI Language/zh_CN ABI/arm32',
            'Referer': 'https://servicewechat.com/wx74767bf0b684f7d3/127/page-frame.html',  # 127?
            'content-type': 'application/json'
        })
    except requests.exceptions.RequestException:
        return False

    try:
        stream_info = res.json()['data']['stream']['flv']['multiLine']

        stream_info = next((item for item in stream_info if item['cdnType'] == preferred_cdn_type), stream_info[0])

        if stream_info['cdnType'] == DISABLED_CDN_TYPE:
            return False

        return stream_info['url']
    except (KeyError, IndexError, ValueError):
        return False


def parse_by_ws(sub_sid, ws_api, preferred_cdn_type):
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        stream_info = loop.run_until_complete(get_stream_ng(sub_sid, ws_api))
    finally:
        asyncio.set_event_loop(None)
        loop.close()

    if not stream_info:
        return False

    stream_info = next((item for item in stream_info if item['sCdnType'] == preferred_cdn_type), stream_info[0])

    if stream_info['sCdnType'] == DISABLED_CDN_TYPE:
        return False

    flv_url = stream_info['sFlvUrl']
    stream_name = stream_info['sStreamName']
    flv_url_suffix = stream_info['sFlvUrlSuffix']
    flv_anti_code = html.unescape(stream_info['sFlvAntiCode'])

    result = f'{flv_url}/{stream_name}.{flv_url_suffix}?{flv_anti_code}'

    # on air
    return result


async def get_stream_ng(sub_sid, ws_api):
    try:
        async with websockets.connect(ws_api) as websocket:
            await websocket.send(array.array('B', get_living_info_request(sub_sid)).tobytes())

            greeting = await asyncio.wait_for(websocket.recv(), timeout=5)
        living_info = get_living_info_response([each for each in greeting])
    except (OSError, ValueError, websockets.exceptions.WebSocketException, asyncio.TimeoutError):
        return False

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
        })
    except requests.exceptions.RequestException:
        return False

    sub_sid_result = sub_sid_pattern.findall(res.text)
    m3u8_result = m3u8_pattern.findall(res.text)

    if m3u8_result:
        return 'https:' + m3u8_result[0].replace('_2000', '')

    if not sub_sid_result:
        return False

    sub_sid = sub_sid_result[0]

    ws_api = random.choice(kwargs['ws_apis']) if 'ws_apis' in kwargs else WS_API
    preferred_cdn_type = kwargs['preferred_cdn_type'] if 'preferred_cdn_type' in kwargs else PREFERRED_CDN_TYPE

    result = parse_by_mini_program(sub_sid, preferred_cdn_type)

    if result:
        return result

    result = parse_by_ws(sub_sid, ws_api, preferred_cdn_type)

    if result:
        return result

    return False


if __name__ == '__main__':
    import time

    while True:
        print(get_stream('668668'))
        time.sleep(5)

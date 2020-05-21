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
NODE_BINARY = 'node'
TAF_COMMAND = NODE_BINARY, os.path.join(pathlib.Path(__file__).parent, 'taf.js')

stream_pattern = re.compile(r'"stream"\s*:\s*({.+?})\s*};')
sub_sid_pattern = re.compile(r'huyalive\\/\d+-(\d+)-')

opener = requests.session()


def get_stream(room_id, **kwargs):
    ws_api = WS_API
    if 'ws_apis' in kwargs:
        ws_api = random.choice(kwargs['ws_apis'])

    preferred_cdn_type = PREFERRED_CDN_TYPE
    if 'preferred_cdn_type' in kwargs:
        preferred_cdn_type = kwargs['preferred_cdn_type']

    try:
        res = opener.get('https://www.huya.com/{0}'.format(room_id))
    except requests.exceptions.RequestException:
        return False

    stream_result = stream_pattern.findall(res.text)
    sub_sid_result = sub_sid_pattern.findall(res.text)

    if not sub_sid_result:
        return False

    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        stream_info = loop.run_until_complete(get_stream_ng(sub_sid_result[0], ws_api))
    finally:
        asyncio.set_event_loop(None)
        loop.close()

    if not stream_info:
        if not stream_result:
            return False

        stream = json.loads(stream_result[0])
        stream_info = stream['data'][0]['gameStreamInfoList']

    stream_info = next((item for item in stream_info if item['sCdnType'] == preferred_cdn_type), stream_info[0])
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


if __name__ == '__main__':
    import time

    while True:
        print(get_stream('nginx'))
        time.sleep(5)

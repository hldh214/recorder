import array
import asyncio
import html
import json
import os
import pathlib
import re
import subprocess

import requests
import websockets

import recorder.ffmpeg as ffmpeg

NODE_BINARY = 'node'
TAF_COMMAND = NODE_BINARY, os.path.join(pathlib.Path(__file__).parent, 'taf.js')

stream_pattern = re.compile(r'"stream"\s*:\s*({.+?})\s*};')
sub_sid_pattern = re.compile(r'huyalive\\/\d+-(\d+)-')

opener = requests.session()


def get_stream(room_id):
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
        stream_info = loop.run_until_complete(get_stream_ng(sub_sid_result[0]))
    finally:
        asyncio.set_event_loop(None)
        loop.close()

    if not stream_info:
        if not stream_result:
            return False

        stream = json.loads(stream_result[0])
        stream_info = stream['data'][0]['gameStreamInfoList'][0]

    flv_url = stream_info['sFlvUrl']
    stream_name = stream_info['sStreamName']
    flv_url_suffix = stream_info['sFlvUrlSuffix']
    flv_anti_code = html.unescape(stream_info['sFlvAntiCode'])

    result = f'{flv_url}/{stream_name}.{flv_url_suffix}?{flv_anti_code}'

    if not ffmpeg.valid(result):
        return False

    # on air
    return result


async def get_stream_ng(sub_sid):
    try:
        async with websockets.connect('wss://wsapi.huya.com') as websocket:
            await websocket.send(array.array('B', get_living_info_request(sub_sid)).tobytes())

            greeting = await asyncio.wait_for(websocket.recv(), timeout=5)
    except (ConnectionResetError, websockets.exceptions.WebSocketException):
        return False

    living_info = get_living_info_response([each for each in greeting])

    if not living_info['bIsLiving']:
        return False

    stream_info = living_info['tNotice']['vStreamInfo']['value']

    if not stream_info:
        return False

    return stream_info[0]


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

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

from recorder.source.tars import tarscore

REQUEST_TIMEOUT = 5
WS_API = 'wss://wsapi.huya.com'
PREFERRED_CDN_TYPE = 'AL'
DISABLED_CDN_TYPE = 'TX'
NODE_BINARY = 'node'
TAF_COMMAND = NODE_BINARY, os.path.join(pathlib.Path(__file__).parent, 'taf.js')

sub_sid_pattern = re.compile(r"ayyuid:\s*'(\d+)'")
m3u8_pattern = re.compile(r"hasvedio\s*:\s*'(\S+)'")
is_live_false_pattern = re.compile(r"var\s*ISLIVE\s*=\s*false")


def parse_by_mini_program(sub_sid, preferred_cdn_type):
    try:
        res = requests.get('https://mp.huya.com/cache.php', params={
            'm': 'Live',
            'do': 'profileRoom',
            'pid': sub_sid,
            'showSecret': '1'
        }, headers={
            'User-Agent': 'Mozilla/5.0 (Linux Android 6.0.1 ALP-AL00 Build/V417IR wv) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.100 Mobile Safari/537.36 '
                          'MicroMessenger/7.0.10.1580(0x27000A59) Process/appbrand0 '
                          'NetType/WIFI Language/zh_CN ABI/arm32',
            'Referer': 'https://servicewechat.com/wx74767bf0b684f7d3/127/page-frame.html',  # 127?
            'content-type': 'application/json'
        }, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.RequestException:
        return False

    try:
        stream_info = res.json()['data']['stream']['flv']['multiLine']

        stream_info = next((item for item in stream_info if item['cdnType'] == preferred_cdn_type), stream_info[0])

        if stream_info['cdnType'] == DISABLED_CDN_TYPE:
            return False

        return stream_info['url']
    except (KeyError, IndexError, ValueError, TypeError):
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
            await websocket.send(array.array('B',
                                             [0, 3, 29, 0, 0, 118, 0, 0, 0, 118, 16, 2, 44, 60, 64, 255, 86, 6, 108,
                                              105, 118, 101, 117, 105, 102, 13, 103, 101, 116, 76, 105, 118, 105, 110,
                                              103, 73, 110, 102, 111, 125, 0, 0, 76, 8, 0, 1, 6, 4, 116, 82, 101, 113,
                                              24, 0, 1, 6, 0, 29, 0, 0, 58, 10, 10, 12, 22, 0, 38, 0, 54, 26, 119, 101,
                                              98, 104, 53, 38, 50, 48, 48, 50, 50, 57, 49, 53, 49, 53, 38, 119, 101, 98,
                                              115, 111, 99, 107, 101, 116, 70, 0, 92, 102, 6, 67, 104, 114, 111, 109,
                                              101, 11, 28, 44, 54, 1, 49, 76, 86, 0, 102, 0, 11, 140, 152, 12, 168, 12]

                                             ).tobytes())

            greeting = await asyncio.wait_for(websocket.recv(), timeout=5)
            print(greeting)
        living_info = get_living_info_response([each for each in greeting])
    except (OSError, ValueError, websockets.exceptions.WebSocketException, asyncio.TimeoutError):
        return False

    print(living_info)
    if not living_info['bIsLiving']:
        return False

    stream_info = living_info['tNotice']['vStreamInfo']['value']

    if not stream_info:
        return False

    return stream_info


class UserId(tarscore.struct):
    __tars_class__ = "HUYA.UserId"

    def __init__(self):
        self.lUid = 0
        self.sGuid = ''
        self.sToken = ''
        self.sHuYaUA = 'webh5&2002291515&websocket'
        self.sCookie = ''
        self.iTokenType = 0
        self.sDeviceInfo = 'Chrome'

    @staticmethod
    def writeTo(oos, value):
        oos.write(tarscore.int32, 0, value.lUid)
        oos.write(tarscore.string, 1, value.sGuid)
        oos.write(tarscore.string, 2, value.sToken)
        oos.write(tarscore.string, 3, value.sHuYaUA)
        oos.write(tarscore.string, 4, value.sCookie)
        oos.write(tarscore.int32, 5, value.iTokenType)
        oos.write(tarscore.string, 6, value.sDeviceInfo)


class GetLivingInfoReq(tarscore.struct):
    __tars_class__ = "HUYA.GetLivingInfoReq"

    def __init__(self, l_sub_sid):
        self.tId = UserId()
        self.iRoomId = 0
        self.lPresenterUid = 0
        self.lSubSid = l_sub_sid
        self.lTopSid = 0
        self.sPassword = ""
        self.sTraceSource = ""

    @staticmethod
    def writeTo(oos, value):
        oos.write(tarscore.struct, 0, value.tId)
        oos.write(tarscore.int32, 1, value.iRoomId)
        oos.write(tarscore.int32, 2, value.lPresenterUid)
        oos.write(tarscore.string, 3, value.lSubSid)
        oos.write(tarscore.int32, 4, value.lTopSid)
        oos.write(tarscore.string, 5, value.sPassword)
        oos.write(tarscore.string, 6, value.sTraceSource)


def get_living_info_request_ng(sub_sid):
    living_info = GetLivingInfoReq(sub_sid)

    wup = tarscore.TarsUniPacket()
    wup.servant = 'liveui'
    wup.func = 'getLivingInfo'
    wup.requestid = -1
    wup.put(tarscore.struct, 'tReq', living_info)

    ws_cmd = tarscore.TarsOutputStream()
    ws_cmd.write(tarscore.int32, 0, 3)  # EWSCmd_WupReq
    ws_cmd.write(tarscore.bytes, 1, wup.encode())

    return ws_cmd.getBuffer()


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
    # m3u8_result = m3u8_pattern.findall(res.text)

    # if m3u8_result and not is_live_false_pattern.findall(res.text):
    #     return 'https:' + m3u8_result[0].replace('_2000', '')

    if not sub_sid_result:
        return False

    sub_sid = sub_sid_result[0]

    ws_api = random.choice(kwargs['ws_apis']) if 'ws_apis' in kwargs else WS_API
    preferred_cdn_type = kwargs['preferred_cdn_type'] if 'preferred_cdn_type' in kwargs else PREFERRED_CDN_TYPE

    # result = parse_by_mini_program(sub_sid, preferred_cdn_type)

    # if result:
    #     return result

    result = parse_by_ws(sub_sid, ws_api, preferred_cdn_type)

    if result:
        return result

    return False


if __name__ == '__main__':
    # dec = tarscore.TarsUniPacket()
    # dd = dec.decode(array.array(
    #     'B',
    #     [0, 3, 29, 0, 0, 116, 0, 0, 0, 116, 16, 3, 44, 60, 64, 255, 86, 6, 108, 105, 118, 101, 117, 105, 102, 13, 103,
    #      101, 116, 76, 105, 118, 105, 110, 103, 73, 110, 102, 111, 125, 0, 0, 74, 8, 0, 1, 6, 4, 116, 82, 101, 113, 29,
    #      0, 0, 61, 10, 10, 12, 22, 0, 38, 0, 54, 26, 119, 101, 98, 104, 53, 38, 50, 48, 48, 50, 50, 57, 49, 53, 49, 53,
    #      38, 119, 101, 98, 115, 111, 99, 107, 101, 116, 70, 0, 92, 102, 6, 67, 104, 114, 111, 109, 101, 11, 28, 32, 1,
    #      60, 70, 4, 110, 117, 108, 108, 86, 0, 108, 11, 140, 152, 12, 168, 12, 35, 0, 0, 0, 0, 0, 0, 0, 0, 54, 9, 117,
    #      110, 100, 101, 102, 105, 110, 101, 100]
    # ))
    # print(dd)
    # exit()

    print(get_living_info_request('1'))
    hex_list = get_living_info_request_ng('1').hex()
    print([int(hex_list[i:i + 2], 16) for i in range(0, len(hex_list), 2)])
    # exit()
    import time

    while True:
        print(get_stream('668668'))
        time.sleep(5)

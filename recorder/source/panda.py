import asyncio
import json
import re
import traceback

import requests
import websockets

WS_COMMAND_TYPE = '42'
LIVE_PLAY_URL = 'https://m.pandalive.co.kr/live/play/?HFX9o9ZQl32zAu2GFv1uthl={room_id}'
ROOMID_PATTERN = re.compile(r'var\s+roomid\s*=\s*String\.fromCharCode\((.+?)\);')


def get_stream(room_id, **kwargs):
    try:
        res = requests.get(LIVE_PLAY_URL.format(room_id=room_id))
    except requests.exceptions.RequestException:
        return False

    room_id_from_char_code = ROOMID_PATTERN.findall(res.text)

    if not room_id_from_char_code:
        return False

    room_id_from_char_code = map(int, str(room_id_from_char_code[0]).split(','))

    stream_info = asyncio.run(get_stream_ng(room_id_from_char_code, kwargs['sess_key']))

    return stream_info


async def get_stream_ng(room_id, sess_key):
    try:
        async with websockets.connect('wss://chat2.neolive.kr/socket.io/?EIO=3&transport=websocket') as websocket:
            # first we receive 2 server hello, just ignore it~
            # 0{"sid":"-uIINngnuEFjn3owCAU5","upgrades":[],"pingInterval":25000,"pingTimeout":5000}
            await asyncio.wait_for(websocket.recv(), timeout=5)
            # 40
            await asyncio.wait_for(websocket.recv(), timeout=5)

            # then we do a initialization, also ignore the server response
            await websocket.send(WS_COMMAND_TYPE + json.dumps([
                "Init",
                {
                    "site": "pandatv",
                    "deviceType": "webMobile",
                    "deviceVersion": "1.0.0",
                    "userAgent": "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, "
                                 "like Gecko) Chrome/80.0.3987.132 Mobile Safari/537.36",
                    "sessKey": sess_key
                }
            ]))
            # 42["Init",{"result":true,"server_name":"blah.blah.blah..."}]
            await asyncio.wait_for(websocket.recv(), timeout=5)

            # after initialization, send a login message
            # and parse `Login` responses
            await websocket.send(WS_COMMAND_TYPE + json.dumps([
                "Login",
                {"sessKey": sess_key, "id": 'just_one_last_dance'}
            ]))
            # 42["Login",{"result":true,"userInfo":{}]
            login_response = await asyncio.wait_for(websocket.recv(), timeout=5)
            logged_in = json.loads(str(login_response).lstrip(WS_COMMAND_TYPE))[1]['result']
            if not logged_in:
                print(login_response)
                return False
            # 42["UserInfo",{"result":true,"userInfo":{}]
            await asyncio.wait_for(websocket.recv(), timeout=5)

            # finally we can send a watch_info request and parse the response
            await websocket.send(WS_COMMAND_TYPE + json.dumps([
                "WatchInfo",
                {"roomid": ''.join(map(chr, room_id)), "action": "watch"}
            ]))

            watch_info_response = await asyncio.wait_for(websocket.recv(), timeout=5)

    except (OSError, ValueError, websockets.exceptions.WebSocketException, asyncio.TimeoutError):
        traceback.print_exc()
        return False

    living_info = json.loads(str(watch_info_response).lstrip(WS_COMMAND_TYPE))[1]

    if not living_info['result']:
        # needUnlimitItem?
        print(living_info)
        return False

    living_info = living_info['PlayList']['hls'][0]['url']

    return living_info


if __name__ == '__main__':
    import time

    while True:
        print(get_stream('10535725', sess_key='018c6d30a09720dd7aba6a9113fa5227bc9c78e033eb1a2be5fec88af599e3c6'))
        time.sleep(5)

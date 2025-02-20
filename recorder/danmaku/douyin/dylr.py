# Credit: https://github.com/LyzenX/DouyinLiveRecorder
import asyncio
import gzip
import hashlib
import logging
import os.path
import random
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

import httpx
import jsengine
import pymongo.errors
import websockets
from google.protobuf import json_format

from recorder import config, mongo_collection_douyin_danmaku as mongo_collection
from recorder.danmaku.douyin.dy_pb2 import PushFrame, Response, ChatMessage
from recorder.source.douyin import get_room_info, get_stream

log_level = logging.INFO
if config['app'].get('debug'):
    log_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(log_level)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'


def build_request_url(url: str, user_agent: str) -> str:
    parsed_url = urlparse(url)
    existing_params = parse_qs(parsed_url.query)
    existing_params['aid'] = ['6383']
    existing_params['device_platform'] = ['web']
    existing_params['browser_language'] = ['zh-CN']
    existing_params['browser_platform'] = ['Win32']
    existing_params['browser_name'] = [user_agent.split('/')[0]]
    existing_params['browser_version'] = [
        user_agent.split(existing_params['browser_name'][0])[-1][1:]]
    new_query_string = urlencode(existing_params, doseq=True)
    new_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        new_query_string,
        parsed_url.fragment
    ))

    return new_url


def get_ms_stub(live_room_real_id, user_unique_id):
    params = {
        "live_id": "1",
        "aid": "6383",
        "version_code": 180800,
        "webcast_sdk_version": '1.0.14-beta.0',
        "room_id": live_room_real_id,
        "sub_room_id": "",
        "sub_channel_id": "",
        "did_rule": "3",
        "user_unique_id": user_unique_id,
        "device_platform": "web",
        "device_type": "",
        "ac": "",
        "identity": "audience"
    }
    sig_params = ','.join([f'{k}={v}' for k, v in params.items()])
    return hashlib.md5(sig_params.encode()).hexdigest()


def auto_get_cookie():
    url = 'https://live.douyin.com'
    cookie = '__ac_nonce=0638733a400869171be51'
    header = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
                  "application/signed-exchange;v=b3;q=0.9",
        "User-Agent": UA,
        "cookie": cookie
    }
    resp = httpx.get(url, headers=header)
    ttwid = None
    for key, value in resp.cookies.items():
        if key == 'ttwid':
            ttwid = value
            break

    if ttwid is not None:
        cookie += '; ttwid=' + ttwid
        return cookie

    return None


def get_danmu_ws_url(id_str):
    # 2024.6.20 接口更新，需要signature参数
    # 代码来源：https://github.com/biliup/biliup/blob/master/biliup/Danmaku/douyin_util/__init__.py
    user_unique_id = random.randint(7300000000000000000, 7999999999999999999)

    with open(os.path.join(os.path.dirname(__file__), 'webmssdk.js'), 'r', encoding='utf-8') as f:
        js_enc = f.read()

    ctx = jsengine.jsengine()
    js_dom = f"""
document = {{}}
window = {{}}
navigator = {{
  'userAgent': '{UA}'
}}
""".strip()
    final_js = js_dom + js_enc
    ctx.eval(final_js)
    function_caller = f"get_sign('{get_ms_stub(id_str, user_unique_id)}')"
    signature = ctx.eval(function_caller)

    webcast5_params = {
        "room_id": id_str,
        "compress": 'gzip',
        "version_code": 180800,
        "webcast_sdk_version": '1.0.14-beta.0',
        "live_id": "1",
        "did_rule": "3",
        "user_unique_id": user_unique_id,
        "identity": "audience",
        "signature": signature,
    }

    return build_request_url(
        f"wss://webcast5-ws-web-lf.douyin.com/webcast/im/push/v2/?{'&'.join([f'{k}={v}' for k, v in webcast5_params.items()])}",
        UA
    )


async def consumer_handler(websocket, room_id):
    room_id = str(room_id)

    while True:
        try:
            ws_msg = await asyncio.wait_for(websocket.recv(), timeout=60)
            print(ws_msg)
        except (TimeoutError) as e:
            logger.error(f'WebSocketException[{e}]: {room_id}')
            break

        wss_package = PushFrame()
        wss_package.ParseFromString(ws_msg)
        decompressed = gzip.decompress(wss_package.payload)
        payload_package = Response()
        payload_package.ParseFromString(decompressed)

        for message in payload_package.messagesList:
            if message.method != 'WebcastChatMessage':
                continue

            chat_message = ChatMessage()
            chat_message.ParseFromString(message.payload)
            data = json_format.MessageToDict(chat_message)

            sender_nick = data['user']['nickName']
            content = data['content']
            msg_id = str(data['common']['msgId'])
            event_time = int(data['eventTime'])

            document = {
                'room_id': room_id,
                'msg_id': msg_id,
                'nickname': sender_nick,
                'content': content,
                'event_time': event_time,
            }

            try:
                mongo_collection.insert_one(document)
            except pymongo.errors.DuplicateKeyError:
                pass
            else:
                logger.info(f'{room_id}: {sender_nick}: {content}')


async def subscribe(room_id, interval):
    logger.info(f'Started danmaku subscriber: {room_id}')

    while True:
        logger.debug(f'Checking live status: {room_id}')
        if not get_stream(room_id):
            # not live yet
            await asyncio.sleep(interval)
            continue

        logger.info(f'Live started: {room_id}')

        room_data = get_room_info(room_id)
        assert 'id_str' in room_data, f'Failed to get id_str, room_data: {room_data}'

        ws_url = get_danmu_ws_url(room_data['id_str'])
        logger.debug(f'ws_url: {ws_url}')

        async with websockets.connect(
            ws_url,
            user_agent_header=UA,
            extra_headers={
                'cookie': auto_get_cookie()
            }
        ) as websocket:
            logger.info(f'Connected to websocket: {room_id}')
        await consumer_handler(websocket, room_id)


async def main():
    sources = [each for each in config.get('source').values() if
               each.get('danmaku_enabled') is True and each['source_type'] == 'douyin']

    tasks = []

    for source in sources:
        tasks.append(asyncio.create_task(subscribe(source['room_id'], source.get('interval', 10))))

    await asyncio.gather(*tasks)

    await asyncio.Future()  # run forever


if __name__ == '__main__':
    asyncio.run(main())

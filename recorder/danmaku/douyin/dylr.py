# Credit: https://github.com/LyzenX/DouyinLiveRecorder
import asyncio
import gzip
import logging
import time

import pymongo.errors
import websockets
from google.protobuf import json_format

from recorder import config, mongo_collection_douyin_danmaku as mongo_collection
from recorder.danmaku.douyin.dy_pb2 import PushFrame, Response, ChatMessage
from recorder.source.douyin import get_room_info, get_stream

log_level = logging.INFO
if config['app'].get('debug'):
    log_level = logging.DEBUG
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=log_level)


def get_danmu_ws_url(id_str):
    return (f"wss://webcast5-ws-web-lf.douyin.com/webcast/im/push/v2/?app_name=douyin_web&version_code=180800"
            f"&webcast_sdk_version=1.0.14-beta.0&update_version_code=1.0.14-beta.0"
            f"&compress=gzip&internal_ext=internal_src:dim"
            f"|wss_push_room_id:{id_str}|wss_push_did:7382749321496675881|dim_log_id"
            f":2023011316221327ACACF0E44A2C0E8200|fetch_time:$"
            f"{int(time.time())}123|seq:1|wss_info:0-1673598133900-0-0|wrds_kvs:WebcastRoomRankMessage"
            f"-1673597852921055645_WebcastRoomStatsMessage-1673598128993068211&cursor=t-1718930306521_r-1_d-1_u-1_fh-1"
            f"&host=https://live.douyin.com&aid=6383&live_id=1&did_rule=3&debug=false&endpoint=live_pc&support_wrds=1"
            f"&im_path=/webcast/im/fetch/&device_platform=web&cookie_enabled=true&screen_width=1228&screen_height=691"
            f"&browser_language=zh-CN&browser_platform=Mozilla&browser_name=Mozilla"
            f"&browser_version=5.0%20(Windows%20NT%2010.0;%20Win64;%20x64)"
            f"%20AppleWebKit/537.36%20(KHTML,%20like%20Gecko)%20Chrome/126.0.0.0%20Safari/537.36"
            f"&browser_online=true&tz_name=Asia/Shanghai"
            f"&identity=audience&room_id={id_str}&heartbeatDuration=0&signature=6dL3Y5Qk0hp77FXh"
            f"&user_unique_id=7382749321496675881")


async def consumer_handler(websocket, room_id):
    room_id = str(room_id)

    while True:
        try:
            ws_msg = await asyncio.wait_for(websocket.recv(), timeout=60)
        except TimeoutError:
            logging.warning(f'No message received in 60 seconds, reconnecting: {room_id}')
            break
        except websockets.WebSocketException:
            logging.warning('WebSocketException excepted')
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
                logging.info(f'{room_id}: {sender_nick}: {content}')


async def subscribe(room_id, interval):
    logging.info(f'Started danmaku subscriber: {room_id}')

    while True:
        logging.debug(f'Checking live status: {room_id}')
        if not get_stream(room_id):
            # not live yet
            await asyncio.sleep(interval)
            continue

        logging.info(f'Live started: {room_id}')

        room_data = get_room_info(room_id)
        assert 'id_str' in room_data, f'Failed to get id_str, room_data: {room_data}'

        ws_url = get_danmu_ws_url(room_data['id_str'])
        logging.debug(f'ws_url: {ws_url}')

        async with websockets.connect(
            ws_url,
            user_agent_header='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/126.0.0.0 Safari/537.36',
            extra_headers={
                # todo: make this cookie configurable
                'cookie': 'ttwid=1%7CB1qls3GdnZhUov9o2NxOMxxYS2ff6OSvEWbv0ytbES4'
                          '%7C1680522049%7C280d802d6d478e3e78d0c807f7c487e7ffec0ae4e5fdd6a0fe74c3c6af149511',
            }
        ) as websocket:
            logging.info(f'Connected to websocket: {room_id}')
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

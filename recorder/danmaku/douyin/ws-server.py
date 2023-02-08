import asyncio
import datetime
import json
import logging
import webbrowser

import pymongo.errors
import websockets

from recorder import mongo_collection_douyin_danmaku as mongo_collection, config
from recorder.source import douyin

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
last_danmaku_time = {}


async def consumer_handler(websocket):
    global last_danmaku_time

    async for message in websocket:
        msg_decoded = json.loads(message)
        room_id = msg_decoded.get('room_id')

        try:
            mongo_collection.insert_one(msg_decoded)
        except pymongo.errors.DuplicateKeyError:
            pass
        else:
            last_danmaku_time[room_id] = datetime.datetime.now()
            if msg_decoded['method'] == 'WebcastChatMessage':
                payload = msg_decoded.get('payload')
                room_id = msg_decoded.get('room_id')
                sender_nick = payload.get('user').get('nickname')
                content = payload.get('content')
                logging.info(f'{room_id}: {sender_nick}: {content}')


async def _main(room_id, interval):
    while True:
        if not douyin.get_stream(room_id):
            # not live yet
            await asyncio.sleep(interval)
            continue

        logging.info(f'Live started: {room_id}')
        webbrowser.open(f'https://live.douyin.com/{room_id}')

        while True:
            await asyncio.sleep(interval)
            if last_danmaku_time[room_id] < datetime.datetime.now() - datetime.timedelta(seconds=60):
                # no danmaku for 60 seconds
                logging.info(f'No danmaku for 60 seconds: {room_id}')
                break


async def main():
    sources = [each for each in config.get('source').values() if
               each.get('danmaku_enabled') is True and each['source_type'] == 'douyin']

    async with websockets.serve(consumer_handler, "localhost", 18964):
        tasks = []

        for source in sources:
            tasks.append(asyncio.create_task(_main(source['room_id'], source.get('interval', 10))))

        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())

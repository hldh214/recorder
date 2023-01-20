import asyncio
import datetime
import json
import logging
import webbrowser

import click
import websockets

from recorder import mongo_collection_douyin_danmaku as mongo_collection
from recorder.source import douyin

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
last_danmaku_time = datetime.datetime.now()


async def consumer_handler(websocket):
    global last_danmaku_time

    async for message in websocket:
        msg_decoded = json.loads(message)
        mongo_collection.insert_one(msg_decoded)
        last_danmaku_time = datetime.datetime.now()
        if msg_decoded['method'] == 'WebcastChatMessage':
            logging.info(msg_decoded['payload']['content'])


async def main(room_id, interval):
    async with websockets.serve(consumer_handler, "localhost", 18964):
        while True:
            if not douyin.get_stream(room_id):
                # not live yet
                await asyncio.sleep(interval)
                continue

            logging.info(f'Live started: {room_id}')
            webbrowser.open(f'https://www.douyu.com/{room_id}')

            while True:
                await asyncio.sleep(interval)
                if last_danmaku_time < datetime.datetime.now() - datetime.timedelta(seconds=60):
                    # no danmaku for 60 seconds
                    logging.info(f'No danmaku for 60 seconds: {room_id}')
                    break

                if not douyin.get_stream(room_id):
                    # live ended
                    logging.info(f'Live ended: {room_id}')
                    break


@click.group()
def cli():
    pass


@cli.command()
@click.option('--room_id', '-r', type=int, required=True)
@click.option('--interval', '-i', type=int, default=10)
def sub(room_id, interval):
    asyncio.run(main(room_id, interval))


if __name__ == '__main__':
    cli()

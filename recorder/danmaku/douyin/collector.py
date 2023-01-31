import asyncio
import datetime
import json
import logging
import random
import re

import click
import playwright.async_api
import pymongo.errors
import websockets

from recorder.source import douyin
from recorder import mongo_collection_douyin_danmaku as mongo_collection

hook_pattern = re.compile(r',\w\.publishSync\((\w+)\)')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
last_danmaku_time = datetime.datetime.now()
js_template = '''
window.data_n = <var_name>;
// get room_id from url
window.data_n.room_id = (new URL(window.location.href)).pathname.split('/')[1];
(() => {
  // pause video player
  if (document.querySelector('.xgplayer-play').getAttribute('data-state') === 'play') {
    document.querySelector('.xgplayer-play').click();
  }
  // disable danmaku display on video player
  if (document.querySelector('.danmu-icon').getAttribute('data-state') === 'active') {
    document.querySelector('.danmu-icon').click();
  }
  // disable gift display on video player
  if (document.querySelectorAll('.fHknbHHl')[2].querySelectorAll('div')[0].innerHTML === '屏蔽礼物特效') {
    document.querySelectorAll('.fHknbHHl')[2].querySelectorAll('div')[1].click();
  }

  if (window.ws_rpc_client && window.ws_rpc_client.readyState !== WebSocket.CLOSED) {
    if (window.ws_rpc_client.readyState === WebSocket.OPEN) {
      window.ws_rpc_client.send(JSON.stringify(window.data_n));
      window.ws_rpc_last_send_time = Date.now();
    }
  } else {
    window.ws_rpc_client = new WebSocket('ws://localhost:<ws_port>');
  }
})();
'''


async def consumer_handler(websocket):
    global last_danmaku_time

    async for message in websocket:
        msg_decoded = json.loads(message)

        try:
            mongo_collection.insert_one(msg_decoded)
        except pymongo.errors.DuplicateKeyError:
            pass
        else:
            last_danmaku_time = datetime.datetime.now()
            if msg_decoded['method'] == 'WebcastChatMessage':
                payload = msg_decoded.get('payload')
                room_id = msg_decoded.get('room_id')
                sender_nick = payload.get('user').get('nickname')
                content = payload.get('content')
                logging.info(f'{room_id}: {sender_nick}: {content}')


async def main(room_id, interval):
    ws_port = random.randint(20000, 30000)

    async with websockets.serve(consumer_handler, "localhost", ws_port):
        while True:
            if not douyin.get_stream(room_id):
                # not live yet
                await asyncio.sleep(interval)
                continue

            logging.info(f'Live started: {room_id}')
            async with playwright.async_api.async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                page = await browser.new_page()

                async def handle_route(route: playwright.async_api.Route):
                    response = await route.fetch()
                    body = await response.text()

                    matches = hook_pattern.finditer(body)
                    for match in matches:
                        full_match = match.group(0)
                        var_name = match.group(1)
                        js_code = js_template.replace('<var_name>', var_name).replace('<ws_port>', str(ws_port))
                        body = body.replace(full_match, f';{js_code}')

                    await route.fulfill(
                        response=response,
                        body=body,
                    )

                await page.route('**/*.js', handle_route)

                try:
                    await page.goto(f'https://live.douyin.com/{room_id}')
                except playwright.async_api.TimeoutError:
                    logging.info(f'Page timeout: {room_id}')
                    await page.close()
                    await browser.close()
                    continue

                title = await page.title()
                logging.info(f'Page loaded: {title}')

                while True:
                    await asyncio.sleep(interval)
                    if last_danmaku_time < datetime.datetime.now() - datetime.timedelta(seconds=60):
                        # no danmaku for 60 seconds
                        logging.info(f'No danmaku for 60 seconds: {room_id}')
                        await page.close()
                        await browser.close()
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

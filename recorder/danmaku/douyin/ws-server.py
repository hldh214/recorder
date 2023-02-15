import asyncio
import datetime
import json
import logging
import pathlib
import re
import urllib.parse
import webbrowser

import playwright.async_api
import pymongo.errors
import websockets

from recorder import mongo_collection_douyin_danmaku as mongo_collection, config
from recorder.source import douyin

log_level = logging.INFO
if config['app'].get('debug'):
    log_level = logging.DEBUG
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=log_level)

last_danmaku_time = {}

hook_pattern = re.compile(r',\w+\.publishSync\((\w+)\)')

js_hook_1 = '''
console.log("======================== Recorder hook start ========================");
window.is_danmaku_dead = false;
window.danmaku_reload_interval = setInterval(() => {
  if (window.ws_rpc_last_send_time) {
    const now = Date.now();
    // if no danmaku in 60s
    if (now - window.ws_rpc_last_send_time > 1000 * 60) {
      console.log("======================== Recorder hook dead ========================");
      window.is_danmaku_dead = true;
      clearInterval(window.danmaku_reload_interval);
    }
  } else {
    // if no danmaku yet
    console.log("======================== Recorder hook dead ========================");
    window.is_danmaku_dead = true;
    clearInterval(window.danmaku_reload_interval);
  }
}, 1000 * 60);
'''
# noinspection SpellCheckingInspection
js_hook_2 = '''
if (!window.is_danmaku_dead) {
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
}
'''


async def get_raw_js(result: asyncio.Future):
    async with playwright.async_api.async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        async def handle_route(route: playwright.async_api.Route):
            response = await route.fetch()
            body = await response.text()

            if hook_pattern.search(body) is not None:
                parsed_url = urllib.parse.urlparse(route.request.url)
                parsed_path = pathlib.PurePath(parsed_url.path.lstrip('/'))
                folder = pathlib.Path(
                    pathlib.Path(__file__).resolve().parent, 'overrides', parsed_url.hostname, parsed_path.parent
                )
                folder.mkdir(parents=True, exist_ok=True)
                file = pathlib.Path(folder, parsed_path.name)
                if not file.exists():
                    with open(file, 'w', encoding='utf-8') as f:
                        f.write(prepare_hook_js(body))
                    logging.info(f'JS File {file} hooked.')
                else:
                    logging.info(f'File {file} already exists, skip writing.')

                result.set_result(True)

            await route.fulfill(
                response=response,
                body=body,
            )

        await page.route('**/*.js', handle_route)

        await page.goto('https://live.douyin.com/590890573')

        if not result.done():
            result.set_result(False)


def prepare_hook_js(raw_js, ws_port=18964):
    result = raw_js.replace('"use strict";', f'"use strict";{js_hook_1}')

    matches = hook_pattern.finditer(result)
    for match in matches:
        full_match = match.group(0)
        var_name = match.group(1)
        js_code = js_hook_2.replace('<var_name>', var_name).replace('<ws_port>', str(ws_port))
        result = result.replace(full_match, f';{js_code}')

    return result


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
    global last_danmaku_time
    last_danmaku_time[room_id] = datetime.datetime.now()
    logging.info(f'Started danmaku subscriber: {room_id}')

    while True:
        logging.debug(f'Checking live status: {room_id}')
        if not douyin.get_stream(room_id):
            # not live yet
            await asyncio.sleep(interval)
            continue

        logging.info(f'Live started: {room_id}')
        hook_result = asyncio.Future()
        asyncio.create_task(get_raw_js(hook_result))
        try:
            result = await asyncio.wait_for(hook_result, 20)
        except TimeoutError:
            logging.error(f'Timeout! Failed to hook js: {room_id}, retrying...')
            continue

        if not result:
            logging.critical(f'Failed to hook js: {room_id}, retrying in 60 seconds')
            await asyncio.sleep(60)
            continue

        webbrowser.open(f'https://live.douyin.com/{room_id}')

        while True:
            logging.debug(f'Still live at [{last_danmaku_time[room_id]}]: {room_id}')
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

        await asyncio.Future()  # run forever


if __name__ == '__main__':
    asyncio.run(main())

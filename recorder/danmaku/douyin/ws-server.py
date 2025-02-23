import asyncio
import datetime
import json
import logging
import pathlib
import re
import time
import urllib.parse
import webbrowser

import playwright.async_api
import pymongo.errors
import websockets

from recorder import mongo_collection_douyin_danmaku as mongo_collection, config
from recorder.source import douyin

ws_port = 18964

log_level = logging.INFO
if config['app'].get('debug'):
    log_level = logging.DEBUG
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=log_level)

last_danmaku_time = {}

hook_pattern = re.compile(r'\("emit async",\S+?,(\w+)\),')

# noinspection SpellCheckingInspection
js_hook_1 = '''
console.log("======================== Recorder hook start ========================");
window.is_danmaku_dead = false;
window.danmaku_reload_interval = setInterval(() => {
  const now = Date.now();
  if (!window.ws_rpc_last_send_time || now - window.ws_rpc_last_send_time > 1000 * 60) {
    console.log("======================== Recorder hook dead ========================");
    window.is_danmaku_dead = true;
    clearInterval(window.danmaku_reload_interval);
  }
}, 1000 * 60);

window.pause_animate = () => {
  // pause video player
  if (document.querySelector('.xgplayer-play').getAttribute('data-state') === 'play') {
    document.querySelector('.xgplayer-play').click();
  }
  // disable danmaku display on video player
  if (document.querySelector('.danmu-icon').getAttribute('data-state') === 'active') {
    document.querySelector('.danmu-icon').click();
  }
  // disable gift display on video player
  let xi = document.getElementsByTagName('xg-icon');
  for (let each_xi of xi) {
    let divs = each_xi.getElementsByTagName('div');
    for (let each_div of divs) {
      if (each_div.innerHTML === '屏蔽礼物特效') {
        let children = each_div.parentElement.children;
        for (let each_child of children) {
          each_child.click();
        }
      }
    }
  }
};

window.pause_animate_timeout = setTimeout(() => {
  window.pause_animate();
}, 4000);

// get room_id from url
window.room_id = (new URL(window.location.href)).pathname.split('/')[1];
'''

# noinspection JSUnresolvedReference
js_hook_2 = '''
if (!window.is_danmaku_dead) {
  let data_array = ["data_array"];
  data_array.forEach((by_type) => {
    by_type[1].forEach((data) => {
      window.ws_rpc_last_send_time = Date.now();

      let payload;
      if (data.method !== "WebcastChatMessage" || data.payload.chat_by != "0") {
        payload = {
          "room_id": window.room_id
        };
      } else {
        payload = {
          "room_id": window.room_id,
          "msg_id": data.msg_id,
          "nickname": data.payload.user.nickname,
          "content": data.payload.content,
          "event_time": parseInt(data.payload.event_time)
        };
      }

      if (window.ws_rpc_client && window.ws_rpc_client.readyState !== WebSocket.CLOSED) {
        if (window.ws_rpc_client.readyState === WebSocket.OPEN) {
          window.ws_rpc_client.send(JSON.stringify(payload));
        }
      } else {
        window.ws_rpc_client = new WebSocket('ws://localhost:<ws_port>');
      }
    });
  });
}
'''.replace('<ws_port>', str(ws_port))


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


def prepare_hook_js(raw_js):
    result = f'{js_hook_1}{raw_js}'  # prepend hook js

    matches = hook_pattern.finditer(result)
    for match in matches:
        full_match = match.group(0)
        var_name = match.group(1)
        js_code = js_hook_2.replace('["data_array"]', var_name)
        result = result.replace(full_match, f'{full_match[:-1]};{js_code}')

    return result


async def consumer_handler(websocket):
    global last_danmaku_time

    async for message in websocket:
        msg_decoded = json.loads(message)
        room_id = msg_decoded.get('room_id')
        sender_nick = msg_decoded.get('nickname')
        content = msg_decoded.get('content')

        if not sender_nick or not content:
            # not danmaku, skip for keepalive
            continue

        last_danmaku_time[room_id] = datetime.datetime.now()
        try:
            mongo_collection.insert_one(msg_decoded)
        except pymongo.errors.DuplicateKeyError:
            pass
        else:
            logging.info(f'{room_id}: {sender_nick}: {content}')


async def _main(room_id, interval):
    logging.info(f'Started danmaku subscriber: {room_id}')

    while True:
        logging.debug(f'Checking live status: {room_id}')
        if not douyin.get_stream(room_id):
            # not live yet
            await asyncio.sleep(interval)
            continue

        logging.info(f'Live started: {room_id}')
        global last_danmaku_time
        last_danmaku_time[room_id] = datetime.datetime.now()
        hook_result = asyncio.Future()
        task = asyncio.create_task(get_raw_js(hook_result))
        try:
            result = await asyncio.wait_for(hook_result, 20)
        except asyncio.exceptions.TimeoutError:
            logging.error(f'Timeout! Failed to hook js: {room_id}, retrying...')
            task.cancel()
            continue

        if not result:
            logging.critical(f'Failed to hook js: {room_id}, retrying in 60 seconds')
            await asyncio.sleep(60)
            continue

        webbrowser.open(f'https://live.douyin.com/{room_id}')
        time.sleep(7)  # wait for page to load
        webbrowser.open(f'https://live.douyin.com/{room_id}')  # I don't know why, but it works

        while True:
            logging.debug(f'Still live at [{last_danmaku_time[room_id]}]: {room_id}')
            await asyncio.sleep(interval)
            if last_danmaku_time[room_id] < datetime.datetime.now() - datetime.timedelta(seconds=120):
                # no danmaku for 120 seconds
                logging.info(f'No danmaku for 120 seconds: {room_id}')
                break


async def main():
    sources = [each for each in config.get('source').values() if
               each.get('danmaku_enabled') is True and each['source_type'] == 'douyin']

    async with websockets.serve(consumer_handler, "localhost", ws_port):
        tasks = []

        for source in sources:
            tasks.append(asyncio.create_task(_main(source['room_id'], source.get('interval', 10))))

        await asyncio.gather(*tasks)

        await asyncio.Future()  # run forever


if __name__ == '__main__':
    asyncio.run(main())

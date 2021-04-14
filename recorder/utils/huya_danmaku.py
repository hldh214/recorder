import asyncio
import json
import os
import time
import urllib.parse
import cachetools
import jwt
import websockets

do_not_pad_flag = '-'
# https://stackoverflow.com/a/28916983/6266737
if os.name == 'nt':
    do_not_pad_flag = '#'

host = 'ws-apiext.huya.com'
iat = int(time.time())
exp = iat + 10 * 60
timestamp_base = 612892800
content_ttl = 5
content_maxsize = 5
show_mode = 0  # 普通弹幕: 0, 上电视: 2
message_notice = 'getMessageNotice'
notice_data = [message_notice]
subscribe_notice = json.dumps({'command': 'subscribeNotice', 'data': notice_data, 'reqId': iat})


async def subscribe(room_id, output_path, app_id, app_secret):
    params = urllib.parse.urlencode({
        'iat': iat,
        'exp': exp,
        'sToken': jwt.encode({'iat': iat, 'exp': exp, 'appId': app_id}, app_secret),
        'appId': app_id,
        'roomId': room_id,
        'do': 'comm',
    })

    # If the corresponding Pong frame isn’t received within ping_timeout seconds,
    # the connection is considered unusable and is closed with code 1011.
    # This ensures that the remote endpoint remains responsive.
    # Set ping_timeout to None to disable this behavior.
    # https://websockets.readthedocs.io/en/stable/api.html#websockets.protocol.WebSocketCommonProtocol
    async with websockets.connect(f'wss://{host}/index.html?{params}', ping_timeout=None) as websocket:
        await websocket.send(subscribe_notice)
        await consumer_handler(websocket, output_path)


async def consumer_handler(websocket, output_path):
    with open(output_path, 'w', encoding='utf8', buffering=1) as fp:
        contents = cachetools.TTLCache(maxsize=content_maxsize, ttl=content_ttl)
        async for message in websocket:
            try:
                message = json.loads(message)
                notice = message['notice']
            except (ValueError, KeyError):
                continue

            if notice != message_notice:
                continue

            if message['data']['showMode'] != show_mode:
                continue

            content = message['data']['content']
            start_seconds = timestamp_base + time.time() - iat
            milliseconds = str(start_seconds)[-3:]

            time_format = f'%{do_not_pad_flag}H:%M:%S.{milliseconds}'
            start = time.strftime(time_format, time.localtime(start_seconds))
            end = time.strftime(time_format, time.localtime(start_seconds + content_ttl))

            ts_pair = f'{start},{end}'
            line = f'{ts_pair}\n{content}\n\n'

            contents[line] = content
            content_list = list(contents.values())
            line = f'{ts_pair}\n'

            for each_content in content_list:
                line += f'{each_content}\n'

            line += '\n'
            fp.write(line)


def main(room_id, output_path, app_id, app_secret):
    asyncio.get_event_loop().run_until_complete(subscribe(room_id, output_path, app_id, app_secret))


if __name__ == '__main__':
    import toml

    config = toml.load('../../config.toml')
    main('11342412', './11342412.sbv', config['huya']['app_id'], config['huya']['app_secret'])

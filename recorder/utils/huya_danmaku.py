import asyncio
import json
import os
import re
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
timestamp_base = 612892800
content_ttl = 4
content_maxsize = 6
show_mode = 0  # 普通弹幕: 0, 上电视: 2
message_notice = 'getMessageNotice'
notice_data = [message_notice]
filter_patterns = [
    r'^/\{',  # 过滤表情开头的弹幕(通常全是表情)
]


def is_spam(content):
    for pattern in filter_patterns:
        if re.match(pattern, content) is not None:
            return True

    return False


async def subscribe(room_id, output_path, app_id, app_secret):
    iat = int(time.time())
    exp = iat + 10 * 60

    params = urllib.parse.urlencode({
        'iat': iat,
        'exp': exp,
        'sToken': jwt.encode({'iat': iat, 'exp': exp, 'appId': app_id}, app_secret),
        'appId': app_id,
        'roomId': room_id,
        'do': 'comm',
    })

    subscribe_notice = json.dumps({'command': 'subscribeNotice', 'data': notice_data, 'reqId': iat})

    # If the corresponding Pong frame isn’t received within ping_timeout seconds,
    # the connection is considered unusable and is closed with code 1011.
    # This ensures that the remote endpoint remains responsive.
    # Set ping_timeout to None to disable this behavior.
    # https://websockets.readthedocs.io/en/stable/api.html#websockets.protocol.WebSocketCommonProtocol
    async with websockets.connect(f'wss://{host}/index.html?{params}', ping_timeout=None) as websocket:
        await websocket.send(subscribe_notice)
        await consumer_handler(websocket, output_path, iat)


async def consumer_handler(websocket, output_path, iat):
    with open(output_path, 'w', encoding='utf8', buffering=1) as fp:
        contents = cachetools.TTLCache(maxsize=content_maxsize, ttl=content_ttl)
        last_start = None
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

            if is_spam(content):
                continue

            start_seconds = timestamp_base + time.time() - iat
            milliseconds = '{:.3f}'.format(start_seconds).split('.')[1]

            time_format = f'%{do_not_pad_flag}H:%M:%S.{milliseconds}'
            start = time.strftime(time_format, time.localtime(start_seconds))
            end = time.strftime(time_format, time.localtime(start_seconds + content_ttl))

            if last_start is not None and last_start >= start:
                continue

            last_start = start

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
    asyncio.run(subscribe(room_id, output_path, app_id, app_secret))


if __name__ == '__main__':
    import sys
    import toml

    room_id = '11342412'
    if len(sys.argv) > 1:
        room_id = sys.argv[1]

    config = toml.load('../../config.toml')
    main(room_id, f'./{room_id}.sbv', config['huya']['app_id'], config['huya']['app_secret'])

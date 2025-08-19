# -*- coding: utf-8 -*-
import asyncio
import http.cookies
import logging
import pathlib
import time
from typing import *

import aiohttp
import arrow

import recorder.danmaku.bilibili.blivedm.blivedm as blivedm
from recorder.danmaku.bilibili.blivedm.blivedm.models import web as web_models

# Integrate with project config and Mongo
import recorder
from recorder import config, mongo_collection_bilibili_danmaku as mongo_collection, TZ_INFO
from recorder.danmaku import parse_datetime, get_info_from_path, Caption
from recorder.destination.youtube import Youtube

logger = logging.getLogger(__name__)

session: Optional[aiohttp.ClientSession] = None

UID_FILTER_LIST = (
    4559060,  # Parnix
)


def _get_bilibili_room_ids_from_config() -> List[int]:
    room_ids: List[int] = []
    for each in config.get('source', {}).values():
        try:
            if each.get('danmaku_enabled') and each.get('source_type') == 'bilibili':
                # room_id might be str in config; store as int
                rid = int(each.get('room_id'))
                room_ids.append(rid)
        except Exception:
            continue
    return room_ids


def _get_sessdata_for_room(room_id: int) -> str:
    # Prefer per-source override if present
    for each in config.get('source', {}).values():
        if str(each.get('room_id')) == str(room_id) and each.get('source_type') == 'bilibili':
            if each.get('sessdata'):
                return str(each.get('sessdata'))
    # Fallback to global [bilibili] section
    return str(config.get('bilibili', {}).get('sessdata', ''))


def _build_session(sessdata: str) -> aiohttp.ClientSession:
    cookies = http.cookies.SimpleCookie()
    if sessdata:
        cookies['SESSDATA'] = sessdata
        cookies['SESSDATA']['domain'] = 'bilibili.com'

    s = aiohttp.ClientSession()
    if sessdata:
        s.cookie_jar.update_cookies(cookies)
    return s


async def _run_client(room_id: int):
    global session
    if session is None:
        # Build using global sessdata if any
        session = _build_session(_get_sessdata_for_room(room_id))

    client = blivedm.BLiveClient(room_id, session=session)
    handler = MyHandler()
    client.set_handler(handler)

    client.start()
    try:
        await client.join()  # run persistently; ws_base handles reconnects
    finally:
        await client.stop_and_close()


async def run_all_clients():
    room_ids = _get_bilibili_room_ids_from_config()
    if not room_ids:
        logger.warning('No Bilibili room_ids with danmaku_enabled found in config. Exiting.')
        return

    # Use a single shared session with global sessdata (if provided)
    global session
    global_sessdata = str(config.get('bilibili', {}).get('sessdata', ''))
    session = _build_session(global_sessdata)

    tasks = [asyncio.create_task(_run_client(rid)) for rid in room_ids]

    # Wait forever until cancelled
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        pass
    finally:
        if session:
            await session.close()


class MyHandler(blivedm.BaseHandler):
    def _on_danmaku(self, client: blivedm.BLiveClient, message: web_models.DanmakuMessage):
        # Persist to MongoDB
        if mongo_collection is None:
            logger.warning('Mongo collection for bilibili danmaku is not configured. Skipping insert.')
            return
        doc = {
            'room_id': client.room_id,
            # message.timestamp is in milliseconds; store as seconds for consistency with other modules
            'event_time': int(message.timestamp // 1000) if message.timestamp else None,
            'uid': message.uid,
            'nickname': message.uname,
            'content': message.msg,
        }
        try:
            mongo_collection.insert_one(doc)
        except Exception as e:
            logger.exception('Failed to insert danmaku for room %s: %r', client.room_id, e)


# =========================
# Query and caption helpers
# =========================

def find_danmaku(room_id, start=None, end=None):
    room_id_int = int(room_id)
    where_clause = {
        'room_id': room_id_int,
        'event_time': {},
        'uid': {'$nin': UID_FILTER_LIST}
    }

    if start:
        where_clause['event_time']['$gt'] = parse_datetime(start).int_timestamp
    if end:
        where_clause['event_time']['$lt'] = parse_datetime(end).int_timestamp

    if not where_clause['event_time']:
        del where_clause['event_time']

    if mongo_collection is None or not mongo_collection.count_documents(where_clause):
        logging.critical(f'Mongo_collection empty, room_id: {room_id}, start: {start}, end: {end}')
        return False

    return mongo_collection.find(where_clause).sort('event_time')


def prepare_iterator_for_caption(danmaku):
    return (
        {
            'generation_time': each.get('event_time'),
            'content': each.get('content'),
        }
        for each in danmaku
    )


def gen_caption_and_return_highlights(room_id, start, end, caption_output_path):
    danmaku = find_danmaku(room_id, start, end)

    assert danmaku is not False

    # store it in memory for reuse
    danmaku_list = list(prepare_iterator_for_caption(danmaku))

    highlights = recorder.danmaku.generate_highlights(danmaku_list, start)

    caption = Caption(danmaku_list, parse_datetime(start))
    caption.to_vtt(caption_output_path)

    return highlights


def add_caption_and_highlights_for_video(caption_path, highlights, video_id, source_config, start):
    youtube = Youtube(config.get('youtube'))

    description = source_config.get('description', '') + '\n\n' + highlights
    title = source_config['title'].format(datetime=start)

    return youtube.add_caption(video_id, caption_path), youtube.update(video_id, title, description)


def watch(room_ids=None):
    where_clause = {
        'event_time': {'$gt': arrow.now().int_timestamp}
    }

    while True:
        if room_ids:
            where_clause.update({'room_id': {'$in': [int(r) for r in room_ids]}})

        cursor = mongo_collection.find(where_clause)

        while cursor.alive:
            for doc in cursor:
                generation_time = arrow.get(doc.get('event_time')).to(TZ_INFO).format('YYYY-MM-DD HH:mm:ss')
                rid = doc.get('room_id')
                sender_nick = doc.get('nickname')
                content = doc.get('content')
                print(f'{generation_time}: {rid}: {sender_nick}: {content}')
                where_clause = {'_id': {'$gt': doc['_id']}}

        time.sleep(1)


def update_video(video_id, room_id=None, start=None, end=None, path=None):
    if room_id and start and end:
        room_id = str(room_id)
        # pick the source config matching this room_id (any platform mix not considered here)
        source_config = next(filter(lambda each: each.get('room_id') == room_id, config.get('source').values()))
        caption_path = f'./{room_id}.vtt'
    elif path:
        source_config, start, end = get_info_from_path(path)
        room_id = source_config['room_id']
        caption_path = f'{pathlib.Path(path).parent}/{video_id}_{start}_{end}.vtt'
    else:
        print('Please provide path or room_id, start, end')
        return

    highlights = gen_caption_and_return_highlights(room_id, start, end, caption_path)

    return add_caption_and_highlights_for_video(caption_path, highlights, video_id, source_config, start)


def generate_ass(video_id, room_id=None, start=None, end=None, path=None):
    if not (path or (room_id and start and end)):
        print('Please provide path or room_id, start, end')
        return

    caption_path = f'./{room_id}.ass'
    if path:
        source_config, start, end = get_info_from_path(path)
        room_id = source_config['room_id']
        caption_path = f'{pathlib.Path(path).parent}/{video_id}_{start}_{end}.ass'

    danmaku = find_danmaku(room_id, start, end)

    assert danmaku is not False

    caption = Caption(prepare_iterator_for_caption(danmaku), parse_datetime(start))
    caption.to_ass(caption_path)


def main():
    try:
        asyncio.run(run_all_clients())
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    import fire

    fire.Fire()

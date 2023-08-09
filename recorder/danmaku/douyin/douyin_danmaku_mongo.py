import logging
import pathlib
import time

import arrow

import recorder
from recorder import config, mongo_collection_douyin_danmaku as mongo_collection, TZ_INFO
from recorder.danmaku import parse_datetime, get_info_from_path, Caption
from recorder.destination.youtube import Youtube


def find_danmaku(room_id, start=None, end=None):
    where_clause = {
        'room_id': room_id,
        'event_time': {}
    }

    if start:
        where_clause['event_time']['$gt'] = parse_datetime(start).int_timestamp
    if end:
        where_clause['event_time']['$lt'] = parse_datetime(end).int_timestamp

    if not where_clause['event_time']:
        del where_clause['event_time']

    if not mongo_collection.count_documents(where_clause):
        logging.critical(f'Mongo_collection empty, room_id: {room_id}, start: {start}, end: {end}')
        return False

    return mongo_collection.find(where_clause)


def prepare_iterator_for_caption(danmaku):
    return (
        {
            'generation_time': each['event_time'],
            'content': each['content'],
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
    while True:
        where_clause = {
            'event_time': {'$gt': arrow.now().int_timestamp}
        }

        if room_ids:
            where_clause.update({'room_id': {'$in': room_ids}})

        cursor = mongo_collection.find(where_clause)

        while cursor.alive:
            for doc in cursor:
                generation_time = arrow.get(doc.get('event_time')).to(TZ_INFO).format('YYYY-MM-DD HH:mm:ss')
                room_id = doc.get('room_id')
                sender_nick = doc.get('nickname')
                content = doc.get('content')
                print(f'{generation_time}: {room_id}: {sender_nick}: {content}')

        time.sleep(1)


def update_video(video_id, room_id=None, start=None, end=None, path=None):
    if room_id and start and end:
        room_id = str(room_id)
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


if __name__ == '__main__':
    import fire

    fire.Fire()

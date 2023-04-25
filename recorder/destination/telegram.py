import functools
import os.path

import tqdm
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import InputMessagesFilterVideo

import recorder.ffmpeg
import recorder.utils


class Telegram:
    def __init__(self, api_id, api_hash, string_session, chat_id):
        self.client = TelegramClient(StringSession(string_session), api_id, api_hash)
        self.client.connect()
        self.chat_id = chat_id

    @staticmethod
    def progress(current, total, pbar, action=None):
        pbar.update(current - pbar.n)

        if action is not None:
            action.progress(current, total)

    def upload(self, path, title):
        with self.client.action(self.chat_id, 'video') as action:
            pbar = tqdm.tqdm(
                total=os.path.getsize(path), desc=f'Uploading [{title}]', unit='B', unit_scale=True, unit_divisor=1024
            )
            progress = functools.partial(self.progress, action=action, pbar=pbar)

            thumb = path + '.thumbnail.jpg'
            if not os.path.exists(thumb):
                # generate video thumbnail
                thumb = recorder.ffmpeg.get_video_thumb(path)

            # noinspection PyTypeChecker
            message = self.client.send_file(
                self.chat_id, path,
                caption=title, silent=True, supports_streaming=True,
                progress_callback=progress, thumb=thumb
            )
            pbar.close()
            os.unlink(thumb)

        return message

    def generate_index(self, message_id=None):
        # get all messages from telegram channel
        # group by source and sum up by views and count
        sources = {}
        top_n = {}
        for message in self.client.iter_messages(self.chat_id, filter=InputMessagesFilterVideo):
            if message.views is None:
                continue
            source = message.text.split('#')[2].split(' ')[0]

            if source not in sources:
                sources[source] = {'views': 0, 'count': 0, 'size': 0, 'duration': 0}
            sources[source]['views'] += message.views
            sources[source]['count'] += 1
            sources[source]['size'] += message.media.document.size
            sources[source]['duration'] += message.media.document.attributes[0].duration

            if source not in top_n:
                top_n[source] = []
            top_n[source].append({
                'views': message.views,
                'message_link': f'https://t.me/{message.chat.username}/{message.id}'
            })

        # sort by views
        sources = sorted(sources.items(), key=lambda x: x[1]['views'], reverse=True)
        top_3 = {k: sorted(v, key=lambda x: x['views'], reverse=True)[:3] for k, v in top_n.items()}

        # generate index
        index = '#Index\n'
        for source in sources:
            index += f'#{source[0]}: {source[1]["views"]} views, {source[1]["count"]} videos, ' \
                     f'{recorder.utils.sizeof_fmt(source[1]["size"])}, ' \
                     f'{source[1]["duration"] // 3600} hours\n'
            for top_x, video in enumerate(top_3[source[0]]):
                index += f'    • [Top{top_x + 1}]({video["message_link"]})\n'

        # send index to telegram channel
        if message_id is not None:
            self.client.edit_message(self.chat_id, message_id, index, link_preview=False)

        return index


if __name__ == '__main__':
    import fire

    from recorder import config

    _app_id = config.get('telegram').get('api_id')
    _api_hash = config.get('telegram').get('api_hash')
    _string_session = config.get('telegram').get('string_session')
    _chat_id = config.get('telegram').get('chat_id')

    telegram = Telegram(_app_id, _api_hash, _string_session, _chat_id)


    def get_string_session():
        with TelegramClient(StringSession(), _app_id, _api_hash) as client:
            print(client.session.save())


    fire.Fire()

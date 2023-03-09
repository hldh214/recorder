import functools
import os.path

import tqdm
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

import recorder.ffmpeg


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

        return message

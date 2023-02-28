import functools

from telethon.sync import TelegramClient
from telethon.sessions import StringSession

import recorder.ffmpeg


class Telegram:
    def __init__(self, api_id, api_hash, string_session, channel_chat_id):
        self.client = TelegramClient(StringSession(string_session), api_id, api_hash)
        self.client.connect()
        self.channel_chat_id = channel_chat_id

    @staticmethod
    def progress(current, total, action=None):
        print('\rUploaded', current, 'out of', total, 'bytes: {:.2%}'.format(current / total), end='', flush=True)

        if action is not None:
            action.progress(current, total)

    def upload(self, path, title):
        with self.client.action(self.channel_chat_id, 'video') as action:
            progress = functools.partial(self.progress, action=action)

            # generate video thumbnail
            thumb = recorder.ffmpeg.get_video_thumb(path)

            # noinspection PyTypeChecker
            message = self.client.send_file(
                self.channel_chat_id, path,
                caption=title, silent=True, supports_streaming=True, progress_callback=progress, thumb=thumb
            )
            print()  # new line

        return message

import datetime
import os
import pathlib
import threading
import time

import toml

import destination.youtube
import ffmpeg
import source.huya

project_root = pathlib.Path(os.path.abspath(__file__)).parent.parent


def get_config(filename='config.toml'):
    return toml.load(os.path.join(project_root, filename))


def record_thread(room_id, sticky_m3u8='', interval=5):
    while True:
        if source.huya.is_live(room_id):
            m3u8_url = source.huya.parse_m3u8(room_id, sticky_m3u8)
            # todo: dont use hard-coded output path
            ffmpeg.record(m3u8_url, os.path.join(
                project_root, 'videos', '{0}/{1}.mp4'.format(room_id, datetime.datetime.now())
            ))
        time.sleep(interval)


def recorder(config):
    # todo: polyfill for all sites
    huya_conf = config['huya']
    for conf in huya_conf.values():
        threading.Thread(target=record_thread, kwargs=conf).start()


def upload_thread():
    pass


def uploader(youtube):
    pass


def validate_thread():
    pass


def validator(youtube):
    pass


def main():
    config = get_config()
    youtube = destination.youtube.Youtube(config)

    recorder(config)

    uploader(youtube)

    validator(youtube)


if __name__ == '__main__':
    main()

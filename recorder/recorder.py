import datetime
import glob
import importlib
import logging
import os
import pathlib
import threading
import time

import toml

import destination.youtube
import ffmpeg

base_path = pathlib.Path(os.path.abspath(__file__)).parent.parent
# todo: dont use hard-coded output path
upload_path = os.path.join(base_path, 'videos', 'upload')
validate_path = os.path.join(base_path, 'videos', 'validate')

logging.basicConfig(
    filename=os.path.join(base_path, 'recorder.log'),
    level=logging.INFO
)


def get_config(filename='config.toml'):
    return toml.load(os.path.join(base_path, filename))


def record_thread(source_type, room_id, name, sticky_m3u8='', interval=5):
    source = importlib.import_module('source.{}'.format(source_type))

    while True:
        if source.is_live(room_id):
            m3u8_url = source.parse_m3u8(room_id, sticky_m3u8)
            ffmpeg.record(m3u8_url, os.path.join(
                upload_path, '{0}/{1}.mp4'.format(name, datetime.datetime.now())
            ))
        time.sleep(interval)


def recorder(config):
    for name, conf in config:
        conf.update({'name': name})

        threading.Thread(
            # todo: whereis the output???
            target=record_thread,
            kwargs=conf,
            name='Recorder-{}'.format(name)
        ).start()


def valid_check_thread(chunk=10 * 3600):
    while True:
        videos = glob.glob(os.path.join(upload_path, '*', '*.mp4'))

        for video_path in videos:
            if not ffmpeg.valid(video_path):
                # unlink that file and save log
                os.unlink(video_path)
                logging.warning('{}: unlinked'.format(video_path))

            duration = ffmpeg.duration(video_path)

            if duration > chunk:
                # need split
                ffmpeg.split(video_path)
                logging.info('{}: split'.format(video_path))


def upload_thread(config, youtube, chunk=10 * 3600):
    while True:
        videos = glob.glob(os.path.join(upload_path, '*', '*.mp4'))

        for video_path in videos:
            duration = ffmpeg.duration(video_path)

            if (not duration) or (duration > chunk):
                continue

            split_video_path = video_path.split(os.sep)
            name = split_video_path[-2]

            video_id = youtube.upload(
                video_path,
                config[name]['title'].format(datetime=datetime.datetime.now()),
                config[name]['description']
            )

            # move to validate folder and add video_id in filename
            os.rename(
                video_path,
                os.path.join(validate_path, '{0}|{1}'.format(
                    video_id, split_video_path[-1]
                ))
            )


def uploader(config, youtube, chunk=10 * 3600):
    threading.Thread(target=valid_check_thread, kwargs={
        'chunk': chunk,
    }).start()

    threading.Thread(target=upload_thread, kwargs={
        'config': config,
        'youtube': youtube,
        'chunk': chunk,
    }).start()


def validate_thread():
    pass


def upload_validator(youtube):
    pass


def main():
    config = get_config()
    youtube = destination.youtube.Youtube(config['youtube'])

    recorder(config['source'])

    uploader(config['source'], youtube)

    # todo
    upload_validator(youtube)


if __name__ == '__main__':
    main()

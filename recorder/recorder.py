import datetime
import glob
import importlib
import logging
import os
import pathlib
import subprocess
import threading
import time

import toml

import destination.youtube
import ffmpeg

video_name_sep = '|'

base_path = pathlib.Path(os.path.abspath(__file__)).parent.parent
# todo: dont use hard-coded output path
upload_path = os.path.join(base_path, 'videos', 'upload')
validate_path = os.path.join(base_path, 'videos', 'validate')

logging.basicConfig(
    filename=os.path.join(base_path, 'recorder.log'),
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s'
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
    for name, conf in config.items():
        conf.update({'name': name})

        threading.Thread(
            # todo: whereis the output???
            target=record_thread,
            kwargs={key: conf[key] for key in (
                'source_type', 'room_id', 'name', 'sticky_m3u8'
            )},
            name='Recorder-{}'.format(name)
        ).start()


def valid_check_thread(chunk=10 * 3600, interval=5):
    while True:
        videos = glob.glob(os.path.join(upload_path, '*', '*.mp4'))

        for video_path in videos:
            if not ffmpeg.valid(video_path):
                # check if this file is in use
                if ffmpeg.in_use(video_path):
                    continue
                # unlink that file and save log
                os.unlink(video_path)
                logging.warning('{}: unlinked'.format(video_path))

            duration = ffmpeg.duration(video_path)

            if duration > chunk:
                # need split
                ffmpeg.split(video_path)
                logging.info('{}: split'.format(video_path))

        time.sleep(interval)


def upload_thread(config, youtube, chunk=10 * 3600, interval=5):
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
            dst_dir = os.path.join(validate_path, name)

            if not os.path.exists(dst_dir):
                os.mkdir(dst_dir)

            os.rename(
                video_path,
                os.path.join(dst_dir, '{0}{1}{2}'.format(
                    video_id, video_name_sep, split_video_path[-1]
                ))
            )

        time.sleep(interval)


def uploader(config, youtube, chunk=10 * 3600):
    threading.Thread(target=valid_check_thread, kwargs={
        'chunk': chunk,
    }).start()

    threading.Thread(target=upload_thread, kwargs={
        'config': config,
        'youtube': youtube,
        'chunk': chunk,
    }).start()


def validate_thread(youtube, interval=360):
    while True:
        videos = glob.glob(os.path.join(validate_path, '*', '*.mp4'))

        for video_path in videos:
            video_id = video_path.split(video_name_sep)[0]

            if youtube.check_uploaded(video_id):
                os.unlink(video_path)
                logging.info('{0}|{1}: uploaded successfully'.format(video_id, video_path))

        time.sleep(interval)


def upload_validator(youtube):
    threading.Thread(target=validate_thread, kwargs={
        'youtube': youtube
    }).start()


def main():
    config = get_config()
    youtube = destination.youtube.Youtube(config['youtube'])

    recorder(config['source'])

    uploader(config['source'], youtube)

    upload_validator(youtube)


if __name__ == '__main__':
    main()

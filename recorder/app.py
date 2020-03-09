import datetime
import glob
import importlib
import logging
import os
import pathlib
import threading
import time

import googleapiclient.errors
import toml

import recorder.destination.youtube
import recorder.ffmpeg as ffmpeg

video_name_sep = '|'

base_path = pathlib.Path(os.path.abspath(__file__)).parent.parent
record_path = os.path.join(base_path, 'videos', 'record')
upload_path = os.path.join(base_path, 'videos', 'upload')
validate_path = os.path.join(base_path, 'videos', 'validate')

logger = logging.getLogger(__name__)
handler = logging.FileHandler(filename=os.path.join(base_path, 'recorder.log'))
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_config(filename='config.toml'):
    return toml.load(os.path.join(base_path, filename))


def record_thread(source_type, room_id, interval=5, **kwargs):
    source = importlib.import_module('recorder.source.{}'.format(source_type))

    while True:
        flv_url = source.get_stream(room_id, **kwargs)
        if flv_url:
            folder_path = os.path.join(record_path, room_id)
            filename = '{0}.flv'.format(datetime.datetime.now())
            pathlib.Path(folder_path).mkdir(parents=True, exist_ok=True)
            output_file = os.path.join(folder_path, filename)

            logger.info(f'recording: {flv_url} -> {output_file}')

            exit_code = ffmpeg.record(flv_url, output_file)

            # move to upload folder
            dst_dir = os.path.join(upload_path, room_id)
            pathlib.Path(dst_dir).mkdir(parents=True, exist_ok=True)
            dst_path = os.path.join(dst_dir, filename)
            os.rename(output_file, dst_path)

            logger.info(f'recorded with exit_code {exit_code}: {flv_url} -> {dst_path}')

        time.sleep(interval)


def my_recorder(config):
    for _, conf in config.items():
        if not conf['enabled']:
            continue

        threading.Thread(
            target=record_thread,
            kwargs=conf
        ).start()


def upload_thread(config, youtube, quota_exceeded_sleep=3600):
    videos = glob.glob(os.path.join(upload_path, '*', '*.flv'))

    for video_path in videos:
        split_video_path = video_path.split(os.sep)
        room_id = split_video_path[-2]
        split_filename = split_video_path[-1].split('.')
        filename_datetime = '{0}'.format('.'.join(split_filename[:-1]))

        logger.info('uploading: {}'.format(video_path))
        try:
            video_id = youtube.upload(
                video_path,
                config[room_id]['title'].format(datetime=filename_datetime),
                config[room_id]['description'] if 'description' in config[room_id] else ''
            )
        except googleapiclient.errors.HttpError as exception:
            logger.warning('A HTTP error occurred:\n{0}'.format(exception))
            continue

        if not video_id:
            # googleapiclient.errors.ResumableUploadError:
            # <HttpError 403 "The request cannot be completed
            # because you have exceeded your
            # <a href="/youtube/v3/getting-started#quota">quota</a>.">
            logger.warning('quota exceeded, sleep {} secs'.format(quota_exceeded_sleep))
            time.sleep(quota_exceeded_sleep)
            continue

        logger.info('uploaded: {}'.format(video_path))

        # move to validate folder and add video_id in filename
        dst_dir = os.path.join(validate_path, room_id)

        pathlib.Path(dst_dir).mkdir(parents=True, exist_ok=True)

        os.rename(
            video_path,
            os.path.join(dst_dir, '{0}{1}{2}'.format(
                video_id, video_name_sep, split_video_path[-1]
            ))
        )


def uploader(config, youtube):
    threading.Thread(target=upload_thread, kwargs={
        'config': config,
        'youtube': youtube
    }).start()


def validate_thread(youtube, interval=360):
    while True:
        videos = glob.glob(os.path.join(validate_path, '*', '*.flv'))

        for video_path in videos:
            split_video_path = video_path.split(os.sep)
            video_id = split_video_path[-1].split(video_name_sep)[0]

            try:
                uploaded = youtube.check_uploaded(video_id)
            except (googleapiclient.errors.HttpError, BrokenPipeError):
                continue

            if uploaded:
                os.unlink(video_path)
                logger.info('uploaded successfully: {0}'.format(video_path))

        time.sleep(interval)


def upload_validator(youtube):
    threading.Thread(target=validate_thread, kwargs={
        'youtube': youtube
    }).start()


def main():
    config = get_config()
    youtube = recorder.destination.youtube.Youtube(config['youtube'])

    my_recorder(config['source'])

    uploader(config['source'], youtube)

    upload_validator(youtube)


if __name__ == '__main__':
    main()

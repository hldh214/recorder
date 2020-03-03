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


def record_thread(source_type, room_id, name, interval=5):
    source = importlib.import_module('recorder.source.{}'.format(source_type))

    while True:
        if source.is_live(room_id):
            flv_url = source.get_stream(room_id)

            folder_path = os.path.join(upload_path, name)
            pathlib.Path(folder_path).mkdir(parents=True, exist_ok=True)

            logger.info(f'recording: {flv_url}')
            exit_code = ffmpeg.record(flv_url, os.path.join(
                folder_path, '{0}.flv'.format(datetime.datetime.now())
            ))
            logger.info(f'recorded with exit_code {exit_code}: {flv_url}')

        time.sleep(interval)


def my_recorder(config):
    for name, conf in config.items():
        if not conf['enabled']:
            continue

        conf.update({'name': name})

        threading.Thread(
            target=record_thread,
            kwargs={key: conf[key] for key in ('source_type', 'room_id', 'name')}
        ).start()


def valid_check_thread(chunk=10 * 3600, interval=5):
    while True:
        videos = glob.glob(os.path.join(upload_path, '*', '*.flv'))

        for video_path in videos:
            if not ffmpeg.valid(video_path):
                # check if this file is in use
                if ffmpeg.in_use(video_path):
                    continue
                # unlink that file and save log
                os.unlink(video_path)
                logger.warning('not valid and unlinked: {}'.format(video_path))

            duration = ffmpeg.duration(video_path)

            if duration > chunk:
                # need split
                # cuz video will be parsed using keyframes, which is very fast
                # so we minus 5 min to insure each chunk size < 10 hrs
                ffmpeg.split(video_path, chunk - 300)
                os.unlink(video_path)
                logger.info('split and unlinked: {}'.format(video_path))

        time.sleep(interval)


def upload_thread(
        config, youtube, chunk=10 * 3600, interval=5,
        quota_exceeded_sleep=3600
):
    while True:
        videos = glob.glob(os.path.join(upload_path, '*', '*.flv'))

        for video_path in videos:
            duration = ffmpeg.duration(video_path)

            if (not duration) or (duration > chunk):
                continue

            split_video_path = video_path.split(os.sep)
            name = split_video_path[-2]
            split_filename = split_video_path[-1].split('.')
            filename_datetime = '{0}'.format('.'.join(split_filename[:-1]))

            logger.info('uploading: {}'.format(video_path))
            try:
                video_id = youtube.upload(
                    video_path,
                    config[name]['title'].format(datetime=filename_datetime),
                    config[name]['description'] if 'description' in config[name] else ''
                )
            except googleapiclient.errors.HttpError as exception:
                time.sleep(interval)
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
            dst_dir = os.path.join(validate_path, name)

            pathlib.Path(dst_dir).mkdir(parents=True, exist_ok=True)

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

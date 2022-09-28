import datetime
import glob
import importlib
import os
import pathlib
import threading
import time
import traceback

import googleapiclient.errors
import pytz

import recorder.destination.youtube
import recorder.ffmpeg as ffmpeg
import recorder.utils.huya_danmaku_mongo as huya_danmaku_mongo
import recorder.utils

from recorder import logger

video_name_sep = '|'
if os.name == 'nt':
    video_name_sep = '__'

video_extension = 'mp4'
vtt_caption_extension = 'vtt'

datetime_format = '%Y-%m-%d %H:%M:%S'
if os.name == 'nt':
    datetime_format = '%Y-%m-%d %H-%M-%S'


def record_thread(source_type, room_id, interval=5, **kwargs):
    source = importlib.import_module(f'recorder.source.{source_type}')

    tz = pytz.timezone(kwargs['app'].get('timezone', 'Asia/Hong_Kong'))

    while True:
        flv_url = source.get_stream(room_id, **kwargs)

        if (not flv_url) or (not ffmpeg.valid(flv_url)):
            time.sleep(interval)
            continue

        folder_path = os.path.join(
            os.path.abspath(kwargs['app']['video_path']), 'record', source_type, kwargs['source_name']
        )
        start = datetime.datetime.now(tz).strftime(datetime_format)
        filename = f'{start}.{video_extension}'
        pathlib.Path(folder_path).mkdir(parents=True, exist_ok=True)
        output_file = os.path.join(folder_path, filename)

        logger.info(f'recording: {flv_url} -> {output_file}')

        exit_code = ffmpeg.record(flv_url, output_file, kwargs['app']['max_duration'])

        if not ffmpeg.valid(output_file):
            if not os.path.exists(output_file):
                logger.warning(f'output_file does not exist: {output_file}')
                continue

            # unlink that file and save log
            os.unlink(output_file)
            logger.warning(f'not valid and unlinked: {output_file}')
            continue

        logger.info(f'recorded with exit_code {exit_code}: {flv_url}')

        if not kwargs.get('auto_upload'):
            continue

        if kwargs.get('auto_upload_minimal_size', 0) > get_file_size(output_file):
            logger.info(f'auto_upload_minimal_size > get_file_size(output_file): {output_file}')
            continue

        if kwargs.get('auto_upload_minimal_duration', 0) > ffmpeg.duration(output_file):
            logger.info(f'auto_upload_minimal_duration > ffmpeg.duration(output_file): {output_file}')
            continue

        # move to upload folder
        dst_dir = os.path.join(
            os.path.abspath(kwargs['app']['video_path']), 'upload', source_type, kwargs['source_name']
        )
        pathlib.Path(dst_dir).mkdir(parents=True, exist_ok=True)
        dst_path = os.path.join(dst_dir, filename)
        os.rename(output_file, dst_path)


def my_recorder(config):
    source = config['source']

    for source_name, conf in source.items():
        if not conf['enabled']:
            continue

        conf.update(config)
        conf['source_name'] = source_name

        task = threading.Thread(
            target=record_thread,
            kwargs=conf,
            name=f'Thread-recorder-{conf["source_type"]}-{conf["room_id"]}'
        )
        task.daemon = True
        task.start()


def upload_thread(config, youtube, interval=5, quota_exceeded_sleep=3600):
    while True:
        videos = glob.glob(os.path.join(
            os.path.abspath(config['app']['video_path']), 'upload', '*', '*', f'*.{video_extension}'
        ))

        for video_path in videos:
            split_video_path = video_path.split(os.sep)
            source_type = split_video_path[-3]
            source_name = split_video_path[-2]
            split_filename = split_video_path[-1].split('.')
            filename_datetime = split_filename[0]

            current_config = config['source'].get(source_name)

            if not current_config:
                continue

            playlist_id = current_config.get('playlist_id')
            room_id = config['source'].get(source_name).get('room_id')
            start = filename_datetime
            end = ffmpeg.calc_end_time(video_path, start, datetime_format)
            highlights = ''
            try:
                highlights = huya_danmaku_mongo.generate_highlights(room_id, start, end)
            except Exception:
                logger.warning('huya_danmaku_mongo.generate_highlights raise exception: ' + traceback.format_exc())

            logger.info(f'uploading: {video_path}')
            try:
                video_id = youtube.upload(
                    video_path,
                    current_config['title'].format(datetime=filename_datetime),
                    current_config.get('description', '') + '\n\n' + highlights,
                )
            except googleapiclient.errors.HttpError as exception:
                time.sleep(interval)
                logger.warning(f'A HTTP error occurred:\n{exception}')
                continue

            if not video_id:
                # googleapiclient.errors.ResumableUploadError:
                # <HttpError 403 "The request cannot be completed
                # because you have exceeded your
                # <a href="/youtube/v3/getting-started#quota">quota</a>.">
                logger.warning(f'quota exceeded, sleep {quota_exceeded_sleep} secs')
                time.sleep(quota_exceeded_sleep)
                continue

            logger.info(f'uploaded: {video_path}')

            if playlist_id:
                youtube.insert_into_playlist(video_id, playlist_id)
                logger.info(f'inserted_into_playlist: {video_id} -> {playlist_id}')

            # move to validate folder and add video_id in filename
            dst_dir = os.path.join(os.path.abspath(config['app']['video_path']), 'validate', source_type, source_name)

            pathlib.Path(dst_dir).mkdir(parents=True, exist_ok=True)

            os.rename(video_path, os.path.join(dst_dir, f'{video_id}{video_name_sep}{split_video_path[-1]}'))

        time.sleep(interval)


def uploader(config, youtube):
    task = threading.Thread(
        target=upload_thread,
        kwargs={'config': config, 'youtube': youtube},
        name='Thread-uploader'
    )
    task.daemon = True
    task.start()


def validate_thread(config, youtube, interval=3600):
    while True:
        videos = glob.glob(os.path.join(
            os.path.abspath(config['app']['video_path']), 'validate', '*', '*', f'*.{video_extension}'
        ))

        for video_path in videos:
            split_video_path = video_path.split(os.sep)
            video_id = split_video_path[-1].split(video_name_sep)[0]
            video_filename = split_video_path[-1].split(video_name_sep)[1]
            source_name = split_video_path[-2]
            source_type = split_video_path[-3]

            caption_folder_path = os.path.join(
                os.path.abspath(config['app']['danmaku_path']), source_type, source_name
            )
            pathlib.Path(caption_folder_path).mkdir(parents=True, exist_ok=True)

            vtt_caption_path = os.path.join(caption_folder_path, f'{video_filename}.{vtt_caption_extension}')
            room_id = config['source'].get(source_name).get('room_id')
            start = video_filename.split('.')[0]
            end = ffmpeg.calc_end_time(video_path, start, datetime_format)

            if config['app']['upload_validate']:
                try:
                    uploaded = youtube.check_processed(video_id)
                except (googleapiclient.errors.HttpError, BrokenPipeError):
                    continue

                if not uploaded:
                    continue

            os.unlink(video_path)
            logger.info(f'uploaded successfully: {video_path}')

            try:
                result = huya_danmaku_mongo.generate(room_id, vtt_caption_path, start, end)
            except Exception:
                logger.warning('huya_danmaku_mongo.generate raise exception: ' + traceback.format_exc())
                continue
            else:
                if not result:
                    logger.warning(f'huya_danmaku_mongo.generate failed: {room_id} {start} {end}')
                    continue

            if os.path.exists(vtt_caption_path):
                if youtube.add_caption(video_id, vtt_caption_path, 'via_recorder_vtt'):
                    os.unlink(vtt_caption_path)
                    logger.info(f'caption added successfully: {vtt_caption_path}')

        time.sleep(interval)


def upload_validator(config, youtube):
    task = threading.Thread(
        target=validate_thread,
        kwargs={'config': config, 'youtube': youtube},
        name='Thread-upload-validator'
    )
    task.daemon = True
    task.start()


def get_file_size(path):
    return float('{:f}'.format(pathlib.Path(path).stat().st_size / 1024 / 1024))


def main():
    config = recorder.utils.get_config()

    my_recorder(config)

    if os.path.exists(config['youtube']['client_secrets_file']):
        youtube = recorder.destination.youtube.Youtube(config['youtube'])

        uploader(config, youtube)

        upload_validator(config, youtube)

    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()

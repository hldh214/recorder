import glob
import logging
import os
import pathlib
import shutil
import time

import click
import opennsfw2 as n2

import recorder.exceptions
from recorder.ffmpeg import generate_candidate_thumbnails
from recorder.utils import sizeof_fmt

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def init_telegram(videos):
    from recorder.destination.telegram import Telegram

    upload_files = []
    for video in videos:
        if os.path.exists(f'{video[0]}.thumbnail.jpg'):
            print(f'Skipping {video[0]}, thumbnail exists')
            upload_files.append(video)
            continue

        thumbs = generate_candidate_thumbnails(video[0], f'{video[0]}.frames')
        if len(thumbs) == 0:
            logger.warning(f'No thumbnails generated for {video[0]}, skipping')
            continue

        logger.info(f'Predicting {video[0]}')
        nsfw_score_list = n2.predict_images(thumbs)
        avg_score = sum(nsfw_score_list) / len(nsfw_score_list)
        max_score = max(nsfw_score_list)
        thumb = thumbs[nsfw_score_list.index(max_score)]
        thumb_filename = thumb.split(os.sep)[-1]  # 32_1888.jpg (32: index, 1888: seconds)
        thumb_second = int(thumb_filename.split('_')[1].split('.')[0])  # 1888
        thumb_time_str = time.strftime('%H:%M:%S', time.gmtime(thumb_second))  # 00:31:28

        logger.info(f'Result: (avg: {avg_score:.4f}, max: {max_score:.4f}({thumb_filename}))')

        if avg_score < 0.1 and max_score < 0.8:
            logger.info(f'Skipping {video[0]}')
            os.rename(video[0], f'{video[0]}.skipped')
            continue

        video[1] += f' (Cover: {thumb_time_str})'
        upload_files.append(video)
        os.rename(thumb, f'{video[0]}.thumbnail.jpg')
        shutil.rmtree(f'{video[0]}.frames')

    return upload_files, Telegram(
        api_id=recorder.config.get('telegram').get('api_id'),
        api_hash=recorder.config.get('telegram').get('api_hash'),
        string_session=recorder.config.get('telegram').get('string_session'),
        chat_id=recorder.config.get('telegram').get('chat_id')
    )


def init_spankbang():
    from recorder.destination.spankbang import Spankbang

    return Spankbang(
        username=recorder.config.get('spankbang').get('username'),
        password=recorder.config.get('spankbang').get('password')
    )


def get_upload_videos(
    source_type,
    filesize_min=1024 * 1024 * 64,
    filesize_max=1024 * 1024 * 2000,
    should_delete_small_files=True
):
    video_path = pathlib.Path(
        recorder.base_path,
        recorder.config.get('app').get('video_path'),
        'record', source_type, '**', '*.mp4'
    )

    files = glob.glob(str(video_path), recursive=True)
    upload_files = []
    delete_files = []

    for file in files:
        # check if recently modified
        if os.path.getmtime(file) > time.time() - 10:
            logger.info(f'{file} is busy, skip')
            continue

        # check file size
        filesize = os.path.getsize(file)
        if filesize < filesize_min:
            logger.warning(f'{file}: {sizeof_fmt(filesize)} < 64MiB, skip')
            delete_files.append(file)
            continue
        if filesize > filesize_max:
            logger.warning(f'{file}: {sizeof_fmt(filesize)} > 2000MiB, skip')
            continue

        path = pathlib.Path(file)
        source_name = path.parent.name
        title = f'#{source_type} #{source_name} `{path.stem}`'
        upload_files.append([file, title])

    print('=' * 64)
    print(f'{len(upload_files)} files found: (64MiB < size < 2000MiB)')
    print('\n'.join([f'{path}: {sizeof_fmt(os.path.getsize(path))}' for path, _ in upload_files]))
    input('press enter to continue... (ctrl+c to cancel)')

    if should_delete_small_files and delete_files:
        print('=' * 64)
        print(f'{len(delete_files)} small files found: (less than 64MiB)')
        print('\n'.join([f'{path}: {sizeof_fmt(os.path.getsize(path))}' for path in delete_files]))
        input('press enter to delete small files... (ctrl+c to cancel)')
        for path in delete_files:
            os.remove(path)

    return upload_files


@click.group()
def cli():
    pass


@cli.command()
@click.option('--source_type', '-s', type=str, required=True)
@click.option('--destination', '-d', type=str, required=True)
def upload(source_type, destination):
    upload_files = get_upload_videos(source_type)

    if destination == 'telegram':
        upload_files, telegram = init_telegram(upload_files)
        upload_function = telegram.upload
    elif destination == 'spankbang':
        upload_function = init_spankbang().upload
    else:
        raise ValueError(f'unknown destination: {destination}')

    assert len(upload_files) > 0, 'no files to upload'

    logger.info(f'uploading {len(upload_files)} files to {destination}')
    print('\n'.join([f'{path} -> {title}' for path, title in upload_files]))
    input('press enter to continue... (ctrl+c to cancel)')

    for index, (path, title) in enumerate(upload_files):
        logger.info(f'uploading {index + 1}/{len(upload_files)}: {path} -> {title}')

        try:
            upload_function(path, title)
        except recorder.exceptions.UploadError as e:
            logger.error(f'upload failed: {e}')

        dst_path = path.replace(f'{os.sep}record{os.sep}', f'{os.sep}validate{os.sep}')
        pathlib.Path(dst_path).parent.mkdir(parents=True, exist_ok=True)
        os.rename(path, dst_path)
        logger.info(f'uploaded {path} -> {dst_path}')


if __name__ == '__main__':
    cli()

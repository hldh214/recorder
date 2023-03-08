import glob
import logging
import os
import pathlib
import time

import click

import recorder.exceptions

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# Credits: https://stackoverflow.com/a/1094933
def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def init_telegram():
    from recorder.destination.telegram import Telegram

    return Telegram(
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


def get_upload_videos(source_type):
    video_path = pathlib.Path(
        recorder.base_path,
        recorder.config.get('app').get('video_path'),
        'record', source_type, '**', '*.mp4'
    )

    files = glob.glob(str(video_path), recursive=True)
    upload_files = []

    for file in files:
        # check if recently modified
        if os.path.getmtime(file) > time.time() - 10:
            logger.info(f'{file} is busy, skip')
            continue

        # check file size
        filesize = os.path.getsize(file)
        if filesize < 1024 * 1024 * 64:
            logger.warning(f'{file}: {sizeof_fmt(filesize)} < 64MiB, skip')
            continue
        # fixme: make this configurable
        if filesize > 1024 * 1024 * 2000:
            logger.warning(f'{file}: {sizeof_fmt(filesize)} > 2000MiB, skip')
            continue

        path = pathlib.Path(file)
        source_name = path.parent.name
        title = f'#{source_type} #{source_name} `{path.stem}`'
        upload_files.append((file, title))

    return upload_files


@click.group()
def cli():
    pass


@cli.command()
@click.option('--source_type', '-s', type=str, required=True)
@click.option('--destination', '-d', type=str, required=True)
def upload(source_type, destination):
    if destination == 'telegram':
        upload_function = init_telegram().upload
    elif destination == 'spankbang':
        upload_function = init_spankbang().upload
    else:
        raise ValueError(f'unknown destination: {destination}')

    upload_files = get_upload_videos(source_type)

    assert len(upload_files) > 0, 'no files to upload'

    logger.info(f'uploading {len(upload_files)} files to {destination}')
    print('\n'.join([f'{path} -> {title}' for path, title in upload_files]))
    input('press enter to continue... (ctrl+c to cancel)')

    for path, title in upload_files:
        logger.info(f'uploading {path} with title {title}')

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

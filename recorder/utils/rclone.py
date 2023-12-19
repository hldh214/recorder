import glob
import json
import logging
import os
import subprocess
import time

import fire

from recorder import config, base_path
from recorder.utils import sizeof_fmt

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def moveto(rname, bwlimit='off'):
    record_folder_path = os.path.join(base_path, config['app']['video_path'], 'record/')

    while True:
        files = glob.glob(str(f'{record_folder_path}/**/*.mp4'), recursive=True)

        for file in files:
            # check if recently modified
            if os.path.getmtime(file) > time.time() - 10:
                logging.info(f'{file} is busy, skip')
                continue

            logging.info(f'Processing {file}: {sizeof_fmt(os.path.getsize(file))}')
            command = [
                'rclone', 'moveto', '--stats-one-line-date', '--progress', '--bwlimit', bwlimit,
                file, f'{rname}:upload/{file.replace(record_folder_path, "")}'
            ]
            logging.info(' '.join(command))
            subprocess.run(command, check=True)
            logging.info(f'Done {file}')

        time.sleep(30)


def list_videos(rname, *args):
    try:
        proc = subprocess.run([
            'rclone', 'lsjson', '--recursive', f'{rname}:upload', *args
        ], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        logging.error(f'Error when listing videos: {e}\n{e.stdout}\n{e.stderr}')
        raise

    files = json.loads(proc.stdout)

    return [f["Path"] for f in files if f['MimeType'] == 'video/mp4']


def watch_and_copy(rname, folder):
    args = ['--min-size', '10M']

    existing_videos = set(list_videos(rname, *args))
    while True:
        time.sleep(120)

        try:
            videos = list_videos(rname, *args)
        except subprocess.CalledProcessError:
            continue

        new_videos = [f for f in videos if f not in existing_videos]

        if not new_videos:
            logging.info('No new videos, skip')
            continue

        for each_video in new_videos:
            logging.info(f'Processing {each_video}')
            command = [
                'rclone', 'copyto', '--progress',
                f'{rname}:upload/{each_video}', f'{folder}/{each_video}'
            ]
            logging.info(' '.join(command))
            subprocess.run(command, check=True)
            logging.info(f'Done {each_video}')

        existing_videos.update([f for f in videos])


if __name__ == '__main__':
    fire.Fire()

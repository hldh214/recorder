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
                'rclone', 'moveto', '--progress', '--bwlimit', bwlimit,
                file, f'{rname}:upload/{file.replace(record_folder_path, "")}'
            ]
            logging.info(' '.join(command))
            subprocess.run(command, check=True)
            logging.info(f'Done {file}')

        time.sleep(30)


def watch_and_copy(rname):
    od_folder_path = os.path.join(base_path, config['app']['video_path'], 'od/')

    existing_videos = set()
    while True:
        proc = subprocess.run([
            'rclone', 'lsjson', '--recursive', f'{rname}:upload'
        ], check=True, capture_output=True)
        files = json.loads(proc.stdout)
        videos = [f for f in files if f['MimeType'] == 'video/mp4']

        new_videos = [f for f in videos if f not in existing_videos]
        for each_video in new_videos:
            logging.info(f'Processing {each_video["Path"]}: {sizeof_fmt(each_video["Size"])}')
            command = [
                'rclone', 'copy', '--progress',
                f'{rname}:upload/{each_video["Path"]}', f'{od_folder_path}/{each_video["Path"]}'
            ]
            logging.info(' '.join(command))
            subprocess.run(command, check=True)
            logging.info(f'Done {each_video["Path"]}')

        existing_videos.update([f for f in videos])
        time.sleep(120)


if __name__ == '__main__':
    fire.Fire()

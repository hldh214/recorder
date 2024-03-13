import glob
import logging
import os
import subprocess
import time

import fire

from recorder import config, base_path
from recorder.utils import sizeof_fmt

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def moveto(rpath):
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
                # The -a will keep permissions, and -h will be humanly readable.
                'rsync', '-ah', '--mkpath', '--progress', file, f'{rpath}/{file.replace(record_folder_path, "")}'
            ]
            logging.info(' '.join(command))
            subprocess.run(command, check=True)
            logging.info(f'Done {file}')

        time.sleep(30)


if __name__ == '__main__':
    fire.Fire()

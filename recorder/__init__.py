import logging
import os
import pathlib

import toml

base_path = pathlib.Path(os.path.abspath(__file__)).parent.parent

config = toml.load(os.path.join(base_path, 'config.toml'))

video_folder_path = os.path.join(base_path, config['app']['video_path'])
caption_folder_path = os.path.join(base_path, config['app']['danmaku_path'])

logger = logging.getLogger(__name__)
handler = logging.FileHandler(filename=os.path.join(base_path, 'recorder.log'))
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

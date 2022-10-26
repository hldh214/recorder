import logging
import os
import pathlib

import toml

datetime_format = '%Y-%m-%d %H:%M:%S'
video_name_sep = '|'
if os.name == 'nt':
    datetime_format = '%Y-%m-%d %H-%M-%S'
    video_name_sep = '__'

base_path = pathlib.Path(os.path.abspath(__file__)).parent.parent

config = toml.load(os.path.join(base_path, 'config.toml'))

logger = logging.getLogger(__name__)
handler = logging.FileHandler(filename=os.path.join(base_path, 'recorder.log'))
logger.setLevel(logging.INFO)
if config['app'].get('debug'):
    logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

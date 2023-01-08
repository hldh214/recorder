import logging
import os
import pathlib

import toml

TZ_INFO = 'Asia/Shanghai'

video_name_sep = '|'
if os.name == 'nt':
    video_name_sep = '__'

ARROW_DATETIME_FORMAT = 'YYYY-MM-DD HH:mm:ss'
if os.name == 'nt':
    ARROW_DATETIME_FORMAT = 'YYYY-MM-DD HH-mm-ss'

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

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
config_path = os.path.join(base_path, 'config.toml')


def get_config():
    return toml.load(config_path)


config = get_config()

httpx_logger = logging.getLogger('httpx')
httpx_logger.setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
handler = logging.FileHandler(filename=os.path.join(base_path, 'recorder.log'))
logger.setLevel(logging.INFO)
if config['app'].get('debug'):
    logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

mongo_client = None
mongo_collection_douyin_danmaku = None
mongo_collection_huya_danmaku = None
mongo_collection_bilibili_danmaku = None
if config['app'].get('mongo_dsn'):
    import pymongo

    mongo_client = pymongo.MongoClient(config['app'].get('mongo_dsn'))
    mongo_collection_douyin_danmaku = mongo_client['recorder']['douyin_danmaku']
    mongo_collection_huya_danmaku = mongo_client['recorder']['huya_danmaku']
    mongo_collection_bilibili_danmaku = mongo_client['recorder']['bilibili_danmaku']

if config['app'].get('sentry_dsn'):
    import sentry_sdk

    sentry_sdk.init(
        dsn=config['app'].get('sentry_dsn'),
        enable_tracing=True,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
    )

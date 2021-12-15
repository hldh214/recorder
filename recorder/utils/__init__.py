import os
import pathlib

import toml


def get_config():
    """
    Get the config file.
    :return: dict
    """
    log_path = os.path.join(pathlib.Path(os.path.abspath(__file__)).parent.parent.parent, 'config.toml')

    assert os.path.exists(log_path), 'Config file not found.'

    return toml.load(log_path)

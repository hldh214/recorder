import logging
import pathlib
import shutil

import click

import recorder.utils as utils

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def get_disk_usage_percent(path):
    usage = shutil.disk_usage(path)

    return int(usage.used / usage.total * 100)


@click.group()
@click.option('--limit', '-l', default=90, type=int)
@click.pass_context
def cli(ctx, limit):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)

    config = utils.get_config()
    video_path = config.get('app').get('video_path')
    df_current = get_disk_usage_percent(video_path)

    if df_current < limit:
        exit()

    ctx.obj['video_path'] = video_path


@cli.command()
@click.pass_context
def unlink_oldest(ctx):
    file_list = pathlib.Path(ctx.obj['video_path']).rglob('*.mp4')
    file_list = sorted(file_list, key=lambda x: x.stat().st_mtime)

    if not file_list:
        logging.warning('No files to unlink')
        return

    file_list[0].unlink(missing_ok=True)
    logging.info(f'Unlinked {file_list[0]}')


if __name__ == '__main__':
    cli(obj={})

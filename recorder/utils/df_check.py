import logging
import os.path
import pathlib
import shutil

import click

import recorder

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def get_disk_usage_percent(path):
    usage = shutil.disk_usage(path)

    return int(usage.used / usage.total * 100)


@click.group()
@click.option('--limit', '-l', default=90, type=int)
@click.option('--ignore_keywords', '-i', default=[], multiple=True, type=str)
@click.pass_context
def cli(ctx, limit, ignore_keywords):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)

    config = recorder.config
    video_folder_path = os.path.join(recorder.base_path, config['app']['video_path'])
    df_current = get_disk_usage_percent(video_folder_path)

    if df_current < limit:
        ctx.exit()

    ctx.obj['video_path'] = video_folder_path
    ctx.obj['ignore_keywords'] = ignore_keywords
    ctx.obj['df_current'] = df_current


@cli.command()
@click.pass_context
def unlink_oldest(ctx):
    # find all videos
    file_list = pathlib.Path(ctx.obj['video_path']).rglob('*.mp4')
    # sort by mtime
    file_list = sorted(file_list, key=lambda x: x.stat().st_mtime)
    # filter out videos with keywords
    file_list = [x for x in file_list if not any(keyword in str(x) for keyword in ctx.obj['ignore_keywords'])]

    if not file_list:
        logging.warning(f'No files to unlink, df_current: {ctx.obj["df_current"]}')
        return

    file_list[0].unlink(missing_ok=True)
    logging.info(f'Unlinked {file_list[0]}')


if __name__ == '__main__':
    cli(obj={})

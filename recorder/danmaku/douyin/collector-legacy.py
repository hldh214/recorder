import logging
import time
import webbrowser

import click

from recorder.source import douyin

chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'


@click.group()
def cli():
    pass


@cli.command()
@click.option('--room_id', '-r', type=int, required=True)
@click.option('--interval', '-i', type=int, default=10)
def sub(room_id, interval):
    while True:
        if not douyin.get_stream(room_id):
            # not live yet
            time.sleep(interval)
            continue

        logging.info(f'Live started: {room_id}')
        webbrowser.get(chrome_path).open(f'https://live.douyin.com/{room_id}')

        while True:
            time.sleep(interval)
            if not douyin.get_stream(room_id):
                # live ended
                logging.info(f'Live ended: {room_id}')
                break


if __name__ == '__main__':
    cli()

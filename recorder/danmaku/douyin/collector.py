import time

import click
from playwright.sync_api import sync_playwright

from recorder.source import douyin


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

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f'https://live.douyin.com/{room_id}')
            print(page.title())
            browser.close()


if __name__ == '__main__':
    cli()

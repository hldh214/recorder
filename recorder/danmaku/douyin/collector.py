import logging
import time

import click
import playwright.sync_api

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

        with playwright.sync_api.sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            def handle_route(route: playwright.sync_api.Route):
                # Fetch original response.
                response = page.request.fetch(route.request)
                # Add a prefix to the title.
                body = response.text()
                logging.info(body)
                # body = body.replace("<title>", "<title>My prefix:")
                route.fulfill(
                    # Pass all fields from the response.
                    response=response,
                    # Override response body.
                    body=body,
                )

            page.route('**/*.js', handle_route)
            page.route("**/*.{png,jpg,jpeg}", lambda route: route.abort())
            page.goto(f'https://live.douyin.com/{room_id}')
            print(page.title())

            while True:
                time.sleep(1)
                if not douyin.get_stream(room_id):
                    # live ended
                    break


if __name__ == '__main__':
    cli()

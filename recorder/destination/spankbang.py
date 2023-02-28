import asyncio

import playwright.async_api

import recorder.exceptions


class Spankbang:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    async def _upload(self, path, title):
        async with playwright.async_api.async_playwright() as p:
            browser = await p.chromium.launch_persistent_context('./spankbang_userdata', headless=False)
            page = await browser.new_page()

            auth_url = 'https://spankbang.com/users/auth'
            await page.goto(auth_url)

            if auth_url == page.url:
                # login
                try:
                    await page.locator('//*[@id="age_check_yes"]').click(timeout=2 * 1000)
                except playwright.async_api.TimeoutError:
                    pass
                await page.locator('//*[@id="auth_register_form"]/ul/li[1]/a').click()
                await page.locator('//*[@id="log_username"]').fill(self.username)
                await page.locator('//*[@id="log_password"]').fill(self.password)
                await page.locator('//*[@id="auth_login_form"]/p[1]/button').click()

            # goto upload
            await page.locator('//*[@id="body-html"]/header/nav/ul/li[1]/a').click()
            file_input = page.locator('//*[@id="fileInput"]')
            await file_input.wait_for(timeout=10 * 1000, state='visible')
            await page.locator('//*[@id="fileInput"]').set_input_files(path)

            # wait until upload finished
            while not await page.locator('//*[@id="upload"]/div/div[3]/p').is_visible():
                progress = await page.locator('//*[@id="form-container-anchor"]/div[5]/div[2]').inner_text()
                est = await page.locator('//*[@id="form-container-anchor"]/div[6]/span[1]').inner_text()
                speed = await page.locator('//*[@id="form-container-anchor"]/div[6]/span[2]').inner_text()
                print(f'\rProgress: {progress}, est: {est}, speed: {speed}', end='', flush=True)

            # fill in video info
            # title
            await page.locator('//*[@id="name_inp"]').fill(title)
            # tags
            tags_input = page.locator('//*[@id="tag_inp"]/div/input')
            await tags_input.type('Korean')
            await page.wait_for_timeout(1000)
            await tags_input.press('Enter')
            await tags_input.type('Korean')
            await page.wait_for_timeout(1000)
            await tags_input.press('Enter')
            # categories
            await page.locator('//*[@id="category_list"]/label[3]').click()  # Asian
            await page.locator('//*[@id="category_list"]/label[13]').click()  # Cam

            # submit
            await page.locator('//*[@id="upload_form_button"]').click()

            i = 0
            while page.url != 'https://spankbang.com/users/videos':
                await page.wait_for_timeout(1000)
                i += 1

                assert i < 16, recorder.exceptions.SpankbangUploadError('upload failed: timeout after 16s')

            await page.close()

    def upload(self, path, title):
        asyncio.run(self._upload(path, title))

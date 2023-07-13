from playwright.sync_api import Page, Playwright

from ..config import CHROME_USER_DATA_DIR, CROME_EXE


def make_pg(playwright_object: Playwright) -> Page:
    browser = playwright_object.chromium.launch_persistent_context(
        executable_path=CROME_EXE,
        user_data_dir=CHROME_USER_DATA_DIR,
        channel="chrome",
        headless=False,
    )
    pg = browser.pages[0]
    pg.set_viewport_size({"width": 1300, "height": 570})

    return pg

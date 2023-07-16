from os import getenv

from dotenv import load_dotenv
from playwright.sync_api import Page, Playwright

from src.config import ACCOUNT_NAME

load_dotenv()

CROME_EXE: str = getenv("CROME_EXE", "")
CHROME_USER_DATA_DIR: str = getenv("CHROME_USER_DATA_DIR", "")

BASE_URL: str = getenv("BASE_URL", "")

EMAIL: str = getenv("EMAIL", "")
PASSWORD: str = getenv("PASSWORD", "")


class BasePage():
    def __init__(self, playwright_object: Playwright) -> None:
        self.pg = self.make_pg(playwright_object)

    def make_pg(self, playwright_object: Playwright) -> Page:
        browser = playwright_object.chromium.launch_persistent_context(
            executable_path=CROME_EXE,
            user_data_dir=CHROME_USER_DATA_DIR,
            channel="chrome",
            headless=False,
        )
        pg = browser.pages[0]
        pg.set_viewport_size({"width": 1300, "height": 570})

        return pg

    def login(self) -> None:
        if self.pg.locator("input[name='email']").is_visible():
            self.pg.fill("input[name='email']", EMAIL)
            self.pg.fill("input[name='password']", PASSWORD)
            self.pg.locator("button", has_text="Entrar").click()
            self.pg.wait_for_url(BASE_URL)

    def select_account(self) -> None:
        account_box = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[2]/div/div/div[1]'
            '/div/div[1]/div[1]/span/button/div/div'
        )
        account_box.click()

        account_labels = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[2]/div/div/div[1]'
            '/div/div[1]/div[2]/div/fieldset/a/div/label/span[1]'
        ).all()
        for account_label in account_labels:
            if account_label.inner_text() == ACCOUNT_NAME:
                account_label.click()

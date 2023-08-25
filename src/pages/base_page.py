from os import getenv

from dotenv import load_dotenv
from playwright.sync_api import Page, Playwright, expect

from src.config import ACCOUNT_NAME

load_dotenv()

CROME_EXE: str = getenv("CROME_EXE", "")
CHROME_USER_DATA_DIR: str = getenv("CHROME_USER_DATA_DIR", "")

BASE_URL = 'https://dashboard.kiwify.com.br/'

EMAIL: str = getenv("EMAIL", "")
PASSWORD: str = getenv("PASSWORD", "")


class BasePage():
    def __init__(self, playwright_object: Playwright) -> None:
        self.pg = self.make_pg(playwright_object)

    def make_pg(self, playwright_object: Playwright) -> Page:
        browser = playwright_object.chromium.launch_persistent_context(
            executable_path=CROME_EXE if CROME_EXE else None,
            user_data_dir=CHROME_USER_DATA_DIR if CHROME_USER_DATA_DIR else '',
            channel="chrome",
            headless=False,
        )
        pg = browser.pages[0]
        pg.set_viewport_size({"width": 1300, "height": 700})
        self.browser = browser

        return pg

    def accept_terms(self) -> None:
        # accept_button = self.pg.locator(
        #     '//*[@id="__layout"]/div/div/div[2]/div/div[2]/div[2]/span/button',
        #     has_text='Aceitar os termos')
        # try:
        #     expect(accept_button).to_be_visible(timeout=4_000)
        #     accept_button.click()
        # except AssertionError:
        #     pass
        ...

    def login(self) -> None:
        if self.pg.locator("input[name='email']").is_visible():
            self.pg.fill("input[name='email']", EMAIL)
            self.pg.fill("input[name='password']", PASSWORD)
            self.pg.locator("button", has_text="Entrar").click()
            self.pg.wait_for_url(BASE_URL)

    def select_account(self) -> None:
        if not ACCOUNT_NAME:
            return

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

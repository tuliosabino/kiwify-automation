import sys
from importlib import import_module
from os import getenv

from dotenv import load_dotenv
from playwright.sync_api import Page, Playwright

from src.config import ACCOUNT_NAME, COURSES, DOMAIN

load_dotenv()

CROME_EXE: str = getenv("CROME_EXE", "")
CHROME_USER_DATA_DIR: str = getenv("CHROME_USER_DATA_DIR", "")

BASE_URL: str = getenv("BASE_URL", "")

EMAIL: str = getenv("EMAIL", "")
PASSWORD: str = getenv("PASSWORD", "")

GET_STRUCTURE_PATH: str = getenv("GET_STRUCTURE_PATH", "")
sys.path.append(GET_STRUCTURE_PATH)
get_structure = getattr(import_module('get_links'), 'get_links')

CREATION_META_PATH: str = getenv("CREATION_META_PATH", "")
sys.path.append(CREATION_META_PATH)
creation_data: dict[str, dict[str, str]] = getattr(
    import_module('courses_creation'), 'course_info')


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

    def create_course(self, course_tag: str,
                      prices: dict[str, int | float]) -> None:
        prod_url = BASE_URL + 'products'
        self.pg.goto(prod_url) if self.pg.url != prod_url else None

        create_course_button = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main'
            '/div[2]/div[2]/div/div[6]/span/div')
        create_course_button.click()

        self.pg.locator('button', has_text='Continuar').click()
        course_metadata = creation_data[course_tag]

        name_field = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]'
            '/div/div[5]/div[2]/div[2]/div/div/div/div[1]/div[2]/div/input')
        name_field.fill(course_metadata['name'])

        description_field = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]'
            '/div/div[5]/div[2]/div[2]/div/div/div/div[1]/div[3]/div/textarea')
        description_field.fill(course_metadata['descrição'])

        prod_url = DOMAIN + course_tag if (
            course_metadata.get('prod_type') != 'Combo') else DOMAIN

        url_field = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]'
            '/div/div[5]/div[2]/div[2]/div/div/div/div[1]/div[4]/div[2]/input')
        url_field.fill(prod_url)

        price_field = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]/div'
            '/div[5]/div[2]/div[2]/div/div/div/div[1]/div[5]/div[1]/div/input')
        price = str(round(float(prices['base_price']), 2))
        price_field.fill(price if len(price) == 5 else price + '0')

        create_button = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]/div'
            '/div[5]/div[2]/div[2]/div/div/div/div[2]/button')
        create_button.click()

        success_message = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[1]/span/div/div/div'
            '/div/div/div[2]/p[1]')
        success_message.wait_for()

    def check_if_course_exists(self, course_tag: str) -> bool:
        self.pg.goto(BASE_URL + 'products')
        course_name = creation_data[course_tag]['name']

        self.pg.wait_for_load_state('networkidle')
        courses_rows_links = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]/div'
            '/div[8]/div/div[3]/div[1]/div/div/table/tbody/tr/td[1]/a'
        ).all()
        courses_list = [(course.inner_text(), course)
                        for course in courses_rows_links]

        for course_text, course_link in courses_list:
            if course_text == course_name:
                course_link.click()
                return True

        return False

    def run(self) -> None:
        self.pg.goto(BASE_URL)
        self.login()

        self.select_account()

        for course_tag, prices in COURSES.items():
            if not self.check_if_course_exists(course_tag):
                self.create_course(course_tag, prices)
            self.pg.goto(BASE_URL) if self.pg.url != BASE_URL else None
        ...

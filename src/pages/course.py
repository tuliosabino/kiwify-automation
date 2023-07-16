import sys
from importlib import import_module
from os import getenv

from dotenv import load_dotenv
from playwright.sync_api import Page

from src.config import (ADDITIONAL_PLAN, COURSES, DOMAIN,
                        PRODUCER_DISPLAY_NAME, SUPPORT_EMAIL)

load_dotenv()

BASE_URL = getenv('BASE_URL', '')
PRODUCT_URL = getenv('PRODUCT_URL', '')

GET_STRUCTURE_PATH: str = getenv("GET_STRUCTURE_PATH", "")
sys.path.append(GET_STRUCTURE_PATH)
get_structure = getattr(import_module('get_links'), 'get_links')

CREATION_META_PATH: str = getenv("CREATION_META_PATH", "")
sys.path.append(CREATION_META_PATH)
creation_data: dict[str, dict[str, str]] = getattr(
    import_module('courses_creation'), 'course_info')


class Course:
    def __init__(self, pg: Page, course_tag: str,) -> None:
        self.tag = course_tag
        self.structure: dict[str, dict[str, str]] = get_structure(course_tag)
        self.pg = pg
        self.meta_data = creation_data[course_tag]
        self.name = self.meta_data['name']
        self.prices: dict[str, int | float] = COURSES[course_tag]
        self.id = None

    def create_product(self) -> None:
        prod_url = BASE_URL + 'products'
        self.pg.goto(prod_url) if self.pg.url != prod_url else None

        create_course_button = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main'
            '/div[2]/div[2]/div/div[6]/span/div')
        create_course_button.click()

        self.pg.locator('button', has_text='Continuar').click()

        name_field = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]'
            '/div/div[5]/div[2]/div[2]/div/div/div/div[1]/div[2]/div/input')
        name_field.fill(self.meta_data['name'])

        description_field = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]'
            '/div/div[5]/div[2]/div[2]/div/div/div/div[1]/div[3]/div/textarea')
        description_field.fill(self.meta_data['descrição'])

        prod_url = DOMAIN + self.tag if (
            self.meta_data.get('prod_type') != 'Combo') else DOMAIN

        url_field = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]'
            '/div/div[5]/div[2]/div[2]/div/div/div/div[1]/div[4]/div[2]/input')
        url_field.fill(prod_url)

        price_field = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]/div'
            '/div[5]/div[2]/div[2]/div/div/div/div[1]/div[5]/div[1]/div/input')
        price = str(round(float(self.prices['base_price']), 2))
        price_field.fill(price if len(price) == 5 else price + '0')

        create_button = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]/div'
            '/div[5]/div[2]/div[2]/div/div/div/div[2]/button')
        create_button.click()

        success_message = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[1]/span/div/div/div'
            '/div/div/div[2]/p[1]')
        success_message.wait_for()

    def check_if_product_exists(self) -> bool:
        self.pg.goto(BASE_URL + 'products')

        search_field = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/'
            'div[2]/div/div[8]/div/div[2]/div[1]/input'
        )
        search_field.fill(self.name)

        courses_rows_links = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]/div'
            '/div[8]/div/div[3]/div[1]/div/div/table/tbody/tr/td[1]/a'
        ).all()
        courses_list = [(course.inner_text(), course)
                        for course in courses_rows_links]

        for course_text, course_link in courses_list:
            if course_text == self.name:
                href = course_link.get_attribute('href')
                self.id = href.split('/')[-1] if href else None
                return True

        return False

    def get_id(self) -> None:
        url = self.pg.url
        id = url.split('/')[-1]
        self.id = id

    def save_product(self) -> None:
        self.pg.locator('button', has_text='Salvar produto').click()

    def create_and_get_id(self) -> None:
        if not self.check_if_product_exists():
            self.create_product()

    def general_settings(self) -> None:
        url = PRODUCT_URL.format(id=self.id)
        self.pg.goto(url) if self.pg.url != url else None

        category = self.meta_data['category_kiwify']
        category_select = self.pg.locator(
            '//*[@id="general"]/div[1]/div/div[2]/div/div/div[3]/div/select'
        )
        category_select.select_option(category)

        image_drop_zone = self.pg.locator(
            '//*[@id="general"]/div[1]/div/div[2]/div/div'
            '/div[4]/div[1]/div[1]/div/button')
        if image_drop_zone.is_visible():
            image_path = self.meta_data['path_to_images'] + r'\600x600.png'
            with self.pg.expect_file_chooser() as fc:
                image_drop_zone.click()
            file_choser = fc.value
            file_choser.set_files(image_path)
            image_sent = self.pg.locator(
                '//*[@id="general"]/div[1]/div/div[2]/div/div/div[4]/img')
            image_sent.wait_for()

        if ADDITIONAL_PLAN:
            check_box_plan = self.pg.locator(
                '//*[@id="general"]/div[2]/div/div[2]/div'
                '/div/div[2]/div[1]/div/span')
            plan_name_field = self.pg.locator(
                '//*[@id="general"]/div[2]/div/div[2]/div/div'
                '/div[2]/div[2]/div[2]/div/div[1]/div/input')
            plan_price_field = self.pg.locator(
                '//*[@id="general"]/div[2]/div/div[2]/div/div/'
                'div[2]/div[2]/div[2]/div/div[2]/div/div/div[1]/input')

            if not plan_name_field.is_visible():
                check_box_plan.click()

            plan_name_field.fill(ADDITIONAL_PLAN)

            price = str(round(float(self.prices['additional']), 2))
            plan_price_field.fill(price if len(price) == 5 else price + '0')

        support_email_field = self.pg.locator(
            '//*[@id="general"]/div[3]/div/div[2]/div'
            '/div/div/div[2]/div/div/input')
        support_email_field.fill(SUPPORT_EMAIL)

        producer_display_name_field = self.pg.locator(
            '//*[@id="general"]/div[3]/div/div[2]/div'
            '/div/div/div[3]/div/div/input')
        producer_display_name_field.fill(PRODUCER_DISPLAY_NAME)

        self.save_product()

    def configs(self) -> None:
        self.general_settings()

        ...

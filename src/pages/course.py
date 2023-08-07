import sys
from importlib import import_module
from os import getenv
from urllib import parse

from dotenv import load_dotenv
from playwright.sync_api import Locator, Page, expect

from src.config import (ADDITIONAL_PLAN, COURSES, DOMAIN, PAYMENT_OPTION,
                        PAYMENT_TIMES, PHONE_NUMBER, PRODUCER_DISPLAY_NAME,
                        SUPPORT_EMAIL, SUPPORT_NUMBER_ON_FIRST_LESSON)

from .base_page import BasePage
from .logging import Logging

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


class Course(BasePage):
    def __init__(self, pg: Page, course_tag: str) -> None:
        self.tag = course_tag
        self.structure: list[dict] = get_structure(course_tag)
        self.pg = pg
        self.meta_data = creation_data[course_tag]
        self.name = self.meta_data['name']
        self.prices: dict[str, int |
                          float] = COURSES[course_tag]  # type: ignore
        self.id = None
        self.logging = Logging(course_tag)

    def create_product(self) -> None:
        prod_url = BASE_URL + 'products'
        self.pg.goto(prod_url) if self.pg.url != prod_url else None
        self.accept_terms()

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
            '//*[@id="__layout"]/div/div/div[1]',
            has_text='Produto criado com sucesso')
        success_message.wait_for()

        self.id = self.pg.url.split('/')[-1]
        self.logging.data[self.tag] = {'id': self.id}
        self.logging.mark_as_done('create_product')

    def check_if_product_exists(self) -> bool:
        self.pg.goto(BASE_URL + 'products')
        self.accept_terms()

        search_field = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/'
            'div[2]/div/div[8]/div/div[2]/div[1]/input'
        )
        search_field.fill(self.name)
        self.pg.wait_for_timeout(500)

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

    def save_product(self) -> None:
        self.pg.locator('button', has_text='Salvar produto').nth(-1).click()

    def create_and_get_id(self) -> None:
        if self.logging.verify_if_done('create_product'):
            self.id = self.logging.data[self.tag]['id']
        else:
            self.create_product()
        # if not self.check_if_product_exists():
        #     self.create_product()

    def general_settings(self) -> None:
        if self.logging.verify_if_done('general_settings'):
            return

        url = PRODUCT_URL.format(id=self.id)
        self.pg.goto(url) if self.pg.url != url else None
        self.accept_terms()

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

            # I have to check the checkbox with the is_visible method because
            # the check method is not working properly
            if not plan_name_field.is_visible():
                check_box_plan.click()

            plan_name_field.fill(ADDITIONAL_PLAN)

            price = str(round(float(self.prices['additional']), 2))
            plan_price_field.clear()
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
        success_message = self.pg.locator(
            '#__layout > div > div > div.flash--wrapper',
            has_text='As alterações do produto foram salvas')
        success_message.wait_for()
        self.logging.mark_as_done('general_settings')

    def payment_and_orderbump_settings(self) -> None:
        if self.logging.verify_if_done('payment_and_orderbump_settings'):
            return

        url = PRODUCT_URL.format(id=self.id) + '?tab=settings'
        self.pg.goto(url) if self.pg.url != url else None
        self.accept_terms()

        payment_select = self.pg.locator(
            '//*[@id="settings"]/div[1]/div/div[2]/div/div/div[1]/div/select')
        payment_select.select_option(PAYMENT_OPTION)

        payment_times_select = self.pg.locator(
            '//*[@id="settings"]/div[1]/div/div[2]/div/div/div[3]/select')
        payment_times_select.select_option(PAYMENT_TIMES)

        def add_order_bump(course_tag: str) -> None:
            course_meta_data = creation_data[course_tag]
            course_name = course_meta_data['name']
            add_order_bump_button = self.pg.locator(
                'button', has_text='Adicionar order bump')
            order_bumps = self.pg.locator(
                '//*[@id="settings"]/div[4]/div/div[2]/div'
                '/div/div[1]/div/div/div/table/tbody/tr'
            ).all()
            if len(order_bumps) >= len(course_meta_data['orderbump']):
                return
            add_order_bump_button.click()

            prod_select = self.pg.locator('//*[@id="vs6__combobox"]')
            prod_select.click()
            prod_select_options = self.pg.locator(
                '//*[@id="vs6__listbox"]/li').all()
            [option.click() for option in prod_select_options
             if option.inner_text() == course_name]

            offer_select = self.pg.locator(
                '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]'
                '/div/div[9]/div/section/div/div[2]/div[2]/div/div/div')
            offer_select.click()
            offer_select_options = self.pg.locator(
                '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]'
                '/div/div[9]/div/section/div/div[2]/div[2]/div/div/ul/li'
            ).all()
            option_to_select = (ADDITIONAL_PLAN
                                if ADDITIONAL_PLAN else course_name)
            [option.click() for option in offer_select_options
             if option.inner_text() == option_to_select]

            title_field = self.pg.locator(
                '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]'
                '/div/div[9]/div/section/div/div[2]/div[4]/div/div/input')
            title_field.fill(course_name)

            description_field = self.pg.locator(
                '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]'
                '/div/div[9]/div/section/div/div[2]/div[5]/div/div/input')
            description_field.fill(course_meta_data['descrição'])

            # I have to check the checkbox with de inner_html method because
            # the check method is not working properly.
            use_image_checkbox = self.pg.locator(
                '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]'
                '/div/div[9]/div/section/div/div[2]/div[6]/div/div/span')
            use_image_checkbox.click() if (
                'translate-x-5' not in use_image_checkbox.inner_html()
            ) else None

            add_button = self.pg.locator(
                '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]'
                '/div/div[9]/div/section/div/div[3]/span[1]/button')
            add_button.click()

            success_message = self.pg.locator(
                '//*[@id="__layout"]/div/div/div[1]',
                has_text='As alterações do produto foram salvas')
            success_message.wait_for()
            close_message_button = self.pg.locator(
                '//*[@id="__layout"]/div/div/div[1]/span/div/div/div/div/div'
                '/div[3]/button')
            close_message_button.click()

        for course_tag in self.meta_data['orderbump']:
            add_order_bump(course_tag)

    def _create_module(self, module: dict) -> None:
        if self.logging.verify_if_done(module['modulo']):
            return

        add_module_button = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]'
            '/div/div[7]/div[1]/div[1]/div[1]/div[2]/a/button'
        )

        add_module_button.click()
        module_name_field = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]'
            '/div[2]/div/div[2]/div/div[2]/div[2]/div/div/div/div[1]'
            '/div/input'
        )
        module_name_field.fill(module.get('modulo', ''))

        class_options = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]'
            '/div/div[2]/div/div[2]/div[2]/div/div/div/div[2]/div/label[1]'
        )
        expect(class_options).to_be_visible()

        all_class_checkbox = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]'
            '/div/div[2]/div/div[2]/div[2]/div/div/div/div[2]/label[2]'
            '/div[1]/input')
        all_class_checkbox.check()

        add_button = self.pg.locator('button', has_text='Adicionar módulo')
        add_button.click()

        self.logging.mark_as_done(module['modulo'])

    def _open_new_form_lesson(self, num_module) -> None:
        self.pg.wait_for_timeout(1000)
        div_container = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]'
            '/div/div[7]/div[1]/div[1]/div[2]/div')

        try:
            expect(div_container).to_be_visible(timeout=5_000)
        except AssertionError:
            pass

        add_content_button = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]'
            f'/div/div[7]/div[1]/div[1]/div[2]/div/div[{num_module + 1}]'
            '/div[2]/div/div[1]'
        )
        add_content_button.click()

        add_content_div = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]/div'
            f'/div[7]/div[1]/div[1]/div[2]/div/div[{num_module + 1}]'
            '/div[2]/div/div[1]/div/div/div/div/div[2]/div/div/div[1]/div[2]'
        )
        add_content_div.click()

    def _insert_lesson_link(self, item: dict) -> None:
        add_link_button = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]'
            '/div[2]/div/div[7]/div[1]/div/div[4]/div[2]/div/div[2]'
            '/div/div/div/div/div/div/div[1]/div/a[7]')
        add_link_button.click()

        insert_link_button = self.pg.locator(
            'a', has_text='Inserir link')
        insert_link_button.click()

        url_field = self.pg.locator('//*[@id="modal-link-url"]')
        url_field.fill(item.get('conteudo', ''))

        text_field = self.pg.locator('//*[@id="modal-link-text"]')
        text_field.fill(item.get('texto_fixo', ''))

        open_in_new_tab_checkbox = self.pg.locator(
            '//html/body/div[7]/div/div[2]/form/div[4]/label/input')
        open_in_new_tab_checkbox.check()

        confirm_insert_button = self.pg.locator(
            '//html/body/div[7]/div/div[3]/button[1]')
        self.pg.wait_for_timeout(500)
        confirm_insert_button.dispatch_event('click')

    def _insert_file(self, file_path: str, locator: Locator) -> None:
        with self.pg.expect_file_chooser() as fc_info:
            locator.click()
        file_chooser = fc_info.value
        file_chooser.set_files(file_path)

    def _fill_lesson_form(self, lesson: dict) -> None:
        title_field = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]'
            '/div/div[7]/div[1]/div/div[4]/div[1]/div/div[2]/div/div'
            '/div[1]/div/input')
        title_field.fill(lesson.get('nome', ''))

        description_field = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]'
            '/div[2]/div/div[7]/div[1]/div/div[4]/div[2]/div/div[2]'
            '/div/div/div/div/div/div/div[2]')

        description_field.click()
        for item in lesson.get('desc_doppus', []):
            if item['tipo'] == 'Link':
                self._insert_lesson_link(item)
            elif item['tipo'] == 'Texto':
                description_field.type(item['conteudo'])

            self.pg.wait_for_timeout(400)
            description_field.press('Control+End')
            self.pg.wait_for_timeout(200)
            description_field.press('Enter')
            self.pg.wait_for_timeout(500)

        upload_video_button = self.pg.locator(
            '//*[@id="uppy-dashboard"]/div/div/div[2]/div/div[2]'
            '/div[2]/div/button')
        with self.pg.expect_file_chooser() as fc_info:
            upload_video_button.click()
        file_chooser = fc_info.value
        file_chooser.set_files(lesson.get('video', ''))

        if lesson.get('files'):
            for file in lesson['files']:
                upload_file_drop_box = self.pg.locator('//*[@id="attachment"]')
                self._insert_file(file, upload_file_drop_box)
                status_upload = self.pg.locator(
                    '//*[@id="attachment"]/div[2]/div/div[2]/div/div')
                expect(status_upload).to_have_attribute(
                    'class', 'uppy-StatusBar is-complete', timeout=180_000)

        if lesson.get('is_bonus'):
            per_day_button = self.pg.locator(
                '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]'
                '/div[2]/div/div[7]/div[1]/div/div[4]/div[4]/div/div[2]'
                '/div/div/div[1]/div/label[2]/input')
            per_day_button.click()

            days_field = self.pg.locator(
                '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]'
                '/div[2]/div/div[7]/div[1]/div/div[4]/div[4]/div/div[2]'
                '/div/div/div[1]/div/label[2]/div/div[2]/div[2]/input')
            days_field.fill('8')

        video_status_div = self.pg.locator(
            '//*[@id="uppy-dashboard"]/div/div/div[2]/div/div[4]')
        expect(video_status_div).to_have_text('Concluído', timeout=600_000)

        submit_button = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]'
            '/div[2]/div/div[7]/div[1]/div/div[5]/div[3]/div')
        submit_button.click()

    def _create_lesson(self, lesson: dict, module: dict, num_module: int,
                       num_lesson: int) -> None:
        if self.logging.verify_if_done(
                f'{module["modulo"]}-{lesson["nome"]}'):
            return

        self._open_new_form_lesson(num_module)

        if (num_module == 0 and num_lesson == 0
                and SUPPORT_NUMBER_ON_FIRST_LESSON):
            course_name = self.meta_data['name']
            phone = ''.join(PHONE_NUMBER.split('-'))
            text = parse.quote(
                f'Olá, preciso de ajuda no curso {course_name}!!',
                safe=',!',
                encoding='UTF-8'
            )
            data = {
                'tipo': 'Link',
                'conteudo': f'https://wa.me/55{phone}/?text={text}',
                'texto_fixo': '>> CLIQUE AQUI E FALE COM O SUPORTE <<'
            }
            lesson['desc_doppus'].insert(0, data)

        self._fill_lesson_form(lesson)

        self.logging.mark_as_done(f'{module["modulo"]}-{lesson["nome"]}')

    def member_content(self) -> None:
        if self.logging.verify_if_done('member_content'):
            return

        url = (BASE_URL + f'products/edit/{self.id}')
        self.pg.goto(url) if self.pg.url != url else None
        self.accept_terms()

        content_link = self.pg.locator(
            '//*[@id="__layout"]/div/div/div[3]/div[3]/main/div[2]/div[2]'
            '/div/div[12]/div/div[1]/nav/div[2]/a'
        )
        expect(content_link).to_have_text('Área de membros', timeout=10_000)

        with self.pg.context.expect_page() as new_page_info:
            content_link.click()
        new_page = new_page_info.value
        self.pg.close()
        self.pg = new_page
        self.pg.set_viewport_size({"width": 1300, "height": 570})

        for num_module, module in enumerate(self.structure):
            self._create_module(module)
            for num_lesson, lesson in enumerate(module['aulas']):
                self._create_lesson(lesson, module, num_module, num_lesson)

        self.logging.mark_as_done('member_content')

    def configs(self) -> None:
        self.general_settings()
        self.member_content()

        ...

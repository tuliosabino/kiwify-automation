from os import getenv

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from src.config import COURSES
from src.pages.base_page import BasePage
from src.pages.course import Course

load_dotenv()

BASE_URL = 'https://dashboard.kiwify.com.br/'


def main():
    with sync_playwright() as p:
        base_page = BasePage(p)
        base_page.pg.goto(BASE_URL)
        base_page.accept_terms()
        base_page.login()

        base_page.select_account()

        for course_tag in COURSES:
            course = Course(base_page.browser.pages[0], course_tag)
            try:
                course.create_and_get_id()
                course.configs()

            finally:
                course.logging.dump()
        ...
        for course_tag in COURSES:
            course = Course(base_page.browser.pages[0], course_tag)
            try:
                course.create_and_get_id()
                course.payment_and_orderbump_settings()

            finally:
                course.logging.dump()


if __name__ == '__main__':
    main()

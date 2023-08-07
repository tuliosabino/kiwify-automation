from os import getenv

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from src.config import COURSES
from src.pages.base_page import BasePage
from src.pages.course import Course

load_dotenv()

BASE_URL = getenv('BASE_URL', '')


def main():
    with sync_playwright() as p:
        browser = BasePage(p)
        browser.pg.goto(BASE_URL)
        browser.accept_terms()
        browser.login()

        browser.select_account()

        for course_tag in COURSES:
            course = Course(browser.pg, course_tag)
            try:
                course.create_and_get_id()
                course.configs()

            finally:
                course.logging.dump()
        ...
        for course_tag in COURSES:
            course = Course(browser.pg, course_tag)
            try:
                course.check_if_product_exists()
                course.payment_and_orderbump_settings()

            finally:
                course.logging.dump()


if __name__ == '__main__':
    main()

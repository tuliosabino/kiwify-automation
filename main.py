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
        browser.login()

        browser.select_account()

        for course_tag in COURSES:
            course = Course(browser.pg, course_tag)
            course.create_and_get_id()
            course.configs()
        ...


if __name__ == '__main__':
    main()

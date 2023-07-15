from playwright.sync_api import sync_playwright

from src.pages.base_page import BasePage


def main():
    with sync_playwright() as p:
        browser = BasePage(p)
        browser.run()


if __name__ == '__main__':
    main()

from playwright.sync_api import sync_playwright

from pages.base_page import make_pg


def main():
    with sync_playwright() as p:
        pg = make_pg(p)
        pg.goto('https://dashboard.kiwify.com.br/')
        ...


if __name__ == '__main__':
    main()

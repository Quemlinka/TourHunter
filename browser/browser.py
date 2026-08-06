from playwright.sync_api import sync_playwright


def open_site():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        print("Открываю сайт...")

        page.goto("https://travelata.ru")

        page.wait_for_timeout(5000)

        browser.close()

        print("Готово!")
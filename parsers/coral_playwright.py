from playwright.sync_api import sync_playwright


class CoralPlaywrightClient:

    SEARCH_URL = "https://www.coral.ru/packagetours/moskva-to-nyachang-tours/"

    def get_best_tour(self):

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=False,
                slow_mo=300,
            )

            page = browser.new_page()

            def handle_response(response):

                try:

                    if (
                        "PackageTourHotelProduct" in response.url
                        or "PriceSearch" in response.url
                    ):

                        print("=" * 80)
                        print(response.url)
                        print(response.status)

                except Exception:
                    pass

            page.on("response", handle_response)

            page.goto(
                self.SEARCH_URL,
                wait_until="domcontentloaded",
                timeout=30000,
            )
            responses = []

def on_response(response):
    url = response.url
    if (
        "PackageTourHotelProduct" in url
        or "api" in url.lower()
        or "_next" in url
    ):
        try:
            text = response.text()
        except Exception:
            return

        if (
            "Golden" in text
            or "price" in text
            or "hotel" in text
            or "result" in text
        ):
            print("=" * 80)
            print(url)
            print(text[:3000])
            print("=" * 80)

            page.on("response", on_response)
            page.wait_for_timeout(2000)

# Закрываем окно выбора города
            try:
                page.get_by_role("button", name="Да").click(timeout=3000)
            except:
                pass

# Закрываем cookies
            try:
                page.get_by_role("button", name="Понятно").click(timeout=3000)
            except:
                pass

            page.wait_for_timeout(1000)
            print(page.url)
            page.locator("button:has-text('Поиск')").click()

            print("\n===== ЖДЕМ 30 СЕКУНД =====\n")

            page.wait_for_timeout(30000)

            print(page.url)
            page.screenshot(path="coral2.png", full_page=True)

            with open(
                "coral.html",
                "w",
                encoding="utf8",
            ) as f:

                f.write(page.content())

            print("\nСкриншот сохранен")

            print("HTML сохранен")

            browser.close()

        return None
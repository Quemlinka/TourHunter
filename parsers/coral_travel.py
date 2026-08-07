"""Browser-based Coral Travel source.

Coral Travel does not expose a public search API.  This adapter therefore uses
the same public search form as a visitor and only consumes data rendered in its
result cards.  A failed Coral check is intentionally isolated by PriceWatcher,
so Travelata monitoring keeps working if the supplier changes its UI.
"""

from __future__ import annotations

import logging
import re
from datetime import date, datetime
from typing import Any

from models.tour import Tour
from tour_config import ADULTS, DATE_FROM, DATE_TO, NIGHTS_FROM, NIGHTS_TO

logger = logging.getLogger(__name__)


class CoralTravelError(RuntimeError):
    pass


class CoralTravel:
    URL = "https://www.coral.ru/top-tours/"
    SOURCE = "Coral Travel"

    def get_best_tour(self) -> Tour | None:
        """Return Coral's cheapest rendered offer matching the configuration."""
        try:
            from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise CoralTravelError(
                "Playwright is not installed. Run: python -m pip install -r requirements.txt"
            ) from exc

        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                try:
                    page = browser.new_page(locale="ru-RU")
                    page.goto(self.URL, wait_until="domcontentloaded", timeout=45_000)
                    self._dismiss_cookie_banner(page)
                    self._set_destination(page)
                    self._set_dates(page)
                    self._set_adults(page)
                    page.get_by_role("button", name="Поиск", exact=True).click()
                    page.wait_for_timeout(2_000)
                    offers = self._offers(page)
                finally:
                    browser.close()
        except PlaywrightTimeoutError as exc:
            raise CoralTravelError("Coral Travel did not return search results in time.") from exc

        matching = [offer for offer in offers if self._matches_configuration(offer)]
        logger.info("Coral Travel: %d matching offers", len(matching))
        return min(matching, key=lambda tour: tour.price, default=None)

    @staticmethod
    def _dismiss_cookie_banner(page: Any) -> None:
        button = page.get_by_role("button", name="Понятно", exact=True)
        if button.count() and button.first.is_visible():
            button.first.click()

    @staticmethod
    def _set_destination(page: Any) -> None:
        # The second search field is the destination on Coral's public form.
        fields = page.locator('input[type="search"]')
        if fields.count() < 2:
            raise CoralTravelError("Coral Travel destination control was not found.")
        destination = fields.nth(1)
        destination.click()
        destination.fill("Нячанг")
        option = page.get_by_text(re.compile(r"Нячанг.*Nha Trang", re.IGNORECASE))
        option.first.wait_for(state="visible", timeout=10_000)
        option.first.click()

    @staticmethod
    def _set_dates(page: Any) -> None:
        """Choose the configured range in Coral's public calendar.

        Day buttons are labelled with ISO date values in the current Coral
        calendar.  Keeping the selectors semantic makes a UI change fail fast
        instead of silently searching a different period.
        """
        date_input = page.get_by_placeholder("Даты вылета")
        date_input.click()
        for value in (DATE_FROM, DATE_TO):
            day = page.get_by_role("button", name=value, exact=True)
            day.first.wait_for(state="visible", timeout=10_000)
            day.first.click()

    @staticmethod
    def _set_adults(page: Any) -> None:
        passengers = page.get_by_label("passenger-label")
        passengers.click()
        current = passengers.input_value()
        # Coral's control displays e.g. "2 взр".  It opens one counter per
        # traveller type; the first decrement applies to adults.
        match = re.search(r"(\d+)\s*взр", current)
        if match is None:
            raise CoralTravelError("Coral Travel passenger control has an unexpected value.")
        difference = int(match.group(1)) - ADULTS
        if difference < 0:
            raise CoralTravelError("Coral Travel opens with fewer adults than requested.")
        for _ in range(difference):
            page.get_by_role("button", name="−", exact=True).first.click()
        page.get_by_role("button", name="Готово", exact=True).click()

    @staticmethod
    def _offers(page: Any) -> list[Tour]:
        cards = page.locator('a[href*="/hotels/"]')
        raw_cards = cards.evaluate_all(
            """links => links.map(link => {
                let element = link;
                while (element.parentElement && !element.innerText.includes('цена от:')) {
                    element = element.parentElement;
                }
                return {url: link.href, text: element.innerText};
            })"""
        )
        tours: list[Tour] = []
        seen: set[str] = set()
        for card in raw_cards:
            tour = _tour_from_card(card)
            if tour is not None and tour.id not in seen:
                seen.add(tour.id)
                tours.append(tour)
        return tours

    @staticmethod
    def _matches_configuration(tour: Tour) -> bool:
        checkin = date.fromisoformat(tour.checkin_date)
        return (
            date.fromisoformat(DATE_FROM) <= checkin <= date.fromisoformat(DATE_TO)
            and NIGHTS_FROM <= tour.tour_nights <= NIGHTS_TO
        )


def _tour_from_card(card: dict[str, str]) -> Tour | None:
    text = card["text"]
    url = card["url"]
    date_match = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", text)
    nights_match = re.search(r"\b(\d+)\s+ноч", text, re.IGNORECASE)
    price_match = re.search(r"цена от:\s*([\d\s]+)\s*₽", text, re.IGNORECASE)
    if not date_match or not nights_match or not price_match:
        return None
    checkin = datetime.strptime(date_match.group(1), "%d/%m/%Y").date().isoformat()
    price = int(re.sub(r"\D", "", price_match.group(1)))
    hotel_name = text.splitlines()[0].strip() or None
    return Tour(
        id=url,
        price=price,
        checkin_date=checkin,
        tour_nights=int(nights_match.group(1)),
        hotel_nights=int(nights_match.group(1)),
        hotel=None,
        resort=None,
        operator=None,
        room=hotel_name,
        source=CoralTravel.SOURCE,
        url=url,
    )

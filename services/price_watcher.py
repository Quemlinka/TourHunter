from __future__ import annotations

from dataclasses import dataclass

from models.tour import Tour
from parsers.travelata_api import TravelataAPI
from services.storage import TourStorage
from tour_config import PRICE_LIMIT


@dataclass(frozen=True, slots=True)
class CheckResult:
    tour: Tour | None
    should_notify: bool
    previous_tour: Tour | None


class PriceWatcher:
    def __init__(self, api: TravelataAPI | None = None, storage: TourStorage | None = None) -> None:
        self.api = api or TravelataAPI()
        self.storage = storage or TourStorage()

    def check_prices(self) -> CheckResult:
        previous = self.storage.load()
        current = self.api.get_best_tour()
        if current is None:
            return CheckResult(tour=None, should_notify=False, previous_tour=previous)

        notify = self._should_notify(previous, current)
        self.storage.save(current)
        return CheckResult(tour=current, should_notify=notify, previous_tour=previous)

    @staticmethod
    def _should_notify(previous: Tour | None, current: Tour) -> bool:
        # The first run establishes a baseline; it does not send a surprise alert.
        if previous is None or current.price > PRICE_LIMIT:
            return False
        if current.identity == previous.identity and current.price == previous.price:
            return False
        return current.price < previous.price or (
            current.identity != previous.identity and current.price <= previous.price
        )

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

from models.tour import Tour
from parsers.coral_travel import CoralTravel
from parsers.travelata_api import TravelataAPI
from services.storage import TourStorage
from tour_config import PRICE_LIMIT


@dataclass(frozen=True, slots=True)
class CheckResult:
    tour: Tour | None
    should_notify: bool
    previous_tour: Tour | None


logger = logging.getLogger(__name__)


class TourSource(Protocol):
    def get_best_tour(self) -> Tour | None: ...


class PriceWatcher:
    def __init__(
        self,
        api: TravelataAPI | None = None,
        storage: TourStorage | None = None,
        sources: tuple[TourSource, ...] | None = None,
    ) -> None:
        # ``api`` is retained for compatibility with the earlier one-source setup.
        self.sources = sources or (api or TravelataAPI(), CoralTravel())
        self.storage = storage or TourStorage()

    def check_prices(self) -> CheckResult:
        previous = self.storage.load()
        candidates: list[Tour] = []
        for source in self.sources:
            try:
                candidate = source.get_best_tour()
            except Exception:
                # A temporary failure of one supplier must not stop alerts from
                # the other supplier.
                logger.exception("Tour source %s failed", type(source).__name__)
                continue
            if candidate is not None:
                candidates.append(candidate)

        current = min(candidates, key=lambda tour: tour.price, default=None)
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

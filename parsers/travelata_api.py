from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any, Iterable, Mapping

import requests

from models.tour import Tour
from tour_config import (
    ADULTS,
    CHILDREN,
    COUNTRY,
    DATE_FROM,
    DATE_TO,
    DEPARTURE_CITY,
    INFANTS,
    NIGHTS_FROM,
    NIGHTS_TO,
    REQUEST_TIMEOUT_SECONDS,
    RESORTS,
    RESULT_LIMIT,
)

logger = logging.getLogger(__name__)


class TravelataAPIError(RuntimeError):
    pass


class TravelataAPI:
    """Small client for Travelata's public search endpoint.

    The endpoint is not an official SDK. Its response is validated defensively
    so an upstream format change results in a clear error instead of bad alerts.
    """

    URL = "https://api-gateway.travelata.ru/frontend/tours"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/150.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://travelata.ru/",
        "Origin": "https://travelata.ru",
    }

    def __init__(self, session: requests.Session | None = None) -> None:
        self._session = session or requests.Session()
        self._session.headers.update(self.HEADERS)

    def get_best_tour(self) -> Tour | None:
        """Return the cheapest valid tour across each date in the configured range."""
        best: Tour | None = None
        for checkin_date in self._dates():
            tours = self.get_tours_for_date(checkin_date.isoformat())
            candidate = min(tours, key=lambda tour: tour.price, default=None)
            if candidate and (best is None or candidate.price < best.price):
                best = candidate
        return best

    def get_tours_for_date(self, checkin_date: str) -> list[Tour]:
        response = self._session.get(
            self.URL,
            params=self._params(checkin_date),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise TravelataAPIError(f"Travelata returned HTTP {response.status_code}.") from exc

        try:
            payload: Any = response.json()
        except ValueError as exc:
            raise TravelataAPIError("Travelata returned an invalid JSON response.") from exc

        raw_tours = _extract_tours(payload)
        tours: list[Tour] = []
        for item in raw_tours:
            try:
                tour = Tour.from_api(item)
            except (KeyError, TypeError, ValueError) as exc:
                logger.debug("Skipping malformed Travelata item: %s", exc)
                continue
            if tour.price > 0 and tour.tour_nights >= NIGHTS_FROM:
                tours.append(tour)
        logger.info("%s: %d valid tours", checkin_date, len(tours))
        return tours

    def _params(self, checkin_date: str) -> list[tuple[str, str | int]]:
        params: list[tuple[str, str | int]] = [
            ("limit", RESULT_LIMIT),
            ("departureCity", DEPARTURE_CITY),
            ("country", COUNTRY),
            ("checkInDateRange[from]", checkin_date),
            ("checkInDateRange[to]", checkin_date),
            ("nightRange[from]", NIGHTS_FROM),
            ("nightRange[to]", NIGHTS_TO),
            ("touristGroup[adults]", ADULTS),
            ("touristGroup[kids]", CHILDREN),
            ("touristGroup[infants]", INFANTS),
            ("priceRange[from]", 1),
            ("priceRange[to]", 21_000_000),
            ("trSm", 1),
        ]
        params.extend(("resorts[]", resort) for resort in RESORTS)
        return params

    @staticmethod
    def _dates() -> Iterable[date]:
        start = date.fromisoformat(DATE_FROM)
        end = date.fromisoformat(DATE_TO)
        if end < start:
            raise ValueError("DATE_TO must not be earlier than DATE_FROM.")
        current = start
        while current <= end:
            yield current
            current += timedelta(days=1)


def _extract_tours(payload: Any) -> list[Mapping[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, Mapping)]
    if not isinstance(payload, Mapping):
        raise TravelataAPIError("Unexpected Travelata response format.")

    # The endpoint currently returns {data: [...]}; earlier versions used
    # {tours: [...]} or {data: {tours: [...]}}. Support all three forms.
    if payload.get("success") is False:
        detail = payload.get("message") or payload.get("error") or "unknown API error"
        raise TravelataAPIError(f"Travelata search failed: {detail}")

    data = payload.get("data")
    result = payload.get("result")
    nested_tours = data.get("tours") if isinstance(data, Mapping) else None
    result_tours = result.get("tours") if isinstance(result, Mapping) else None
    result_data = result.get("data") if isinstance(result, Mapping) else None
    candidates = (
        result if isinstance(result, list) else None,
        payload.get("tours"),
        data if isinstance(data, list) else None,
        nested_tours,
        result_tours,
        result_data if isinstance(result_data, list) else None,
        payload.get("items"),
    )
    for value in candidates:
        if isinstance(value, list):
            return [item for item in value if isinstance(item, Mapping)]
    keys = ", ".join(str(key) for key in payload.keys())
    raise TravelataAPIError(
        f"Travelata response does not contain a tours list (keys: {keys})."
    )
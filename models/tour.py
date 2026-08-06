from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class Tour:
    """A normalized tour returned by Travelata's search endpoint."""

    id: str
    price: int
    checkin_date: str
    tour_nights: int
    hotel_nights: int
    hotel: int | None
    resort: int | None
    operator: int | None
    room: str | None = None
    transfer: str | None = None

    @property
    def identity(self) -> str:
        """Stable enough to suppress repeated notifications for one offer."""
        return self.id or ":".join(
            str(value)
            for value in (self.checkin_date, self.tour_nights, self.hotel, self.operator, self.room)
        )

    @classmethod
    def from_api(cls, item: Mapping[str, Any]) -> "Tour":
        nights = item.get("nights") or {}
        return cls(
            id=str(item.get("id") or ""),
            price=int(item["price"]),
            checkin_date=str(item["checkInDate"]),
            tour_nights=int(nights.get("tour", 0)),
            hotel_nights=int(nights.get("hotel", 0)),
            hotel=_as_int(item.get("hotel")),
            resort=_as_int(item.get("resort")),
            operator=_as_int(item.get("operator")),
            room=_as_text(item.get("room")),
            transfer=_as_text(item.get("transfer")),
        )


def _as_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _as_text(value: Any) -> str | None:
    return str(value) if value is not None else None

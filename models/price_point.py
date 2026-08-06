from dataclasses import dataclass


@dataclass
class PricePoint:
    checkin_date: str
    price: int | None
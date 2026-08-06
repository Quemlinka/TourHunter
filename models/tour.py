from dataclasses import dataclass


@dataclass
class Tour:
    country: str
    city: str
    hotel: str
    stars: int
    nights: int
    departure_city: str
    departure_date: str
    price: int
    url: str
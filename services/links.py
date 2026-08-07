from __future__ import annotations

from models.tour import Tour


def tour_search_url(tour: Tour) -> str:
    """Return the public page on which the offer can be opened again."""
    if tour.url:
        return tour.url
    if tour.source == "Coral Travel":
        return "https://www.coral.ru/top-tours/"
    return travelata_search_url(tour)


def tour_source_label(tour: Tour) -> str:
    return tour.source


def travelata_search_url(tour: Tour) -> str:
    """Return the stable public Travelata search page.

    Travelata's API offer IDs are internal, temporary values and are not valid
    public booking links. The public search page is consequently safer than a
    fabricated deep link: the alert already gives the exact date and nights.
    """
    del tour
    return "https://travelata.ru/search"

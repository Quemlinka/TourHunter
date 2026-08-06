from models.tour import Tour


def find_best_tour():
    return Tour(
        country="Вьетнам",
        city="Нячанг",
        hotel="Regalia Gold",
        stars=5,
        nights=8,
        departure_city="Москва",
        departure_date="28.08.2026",
        price=63900,
        url="https://example.com"
    )
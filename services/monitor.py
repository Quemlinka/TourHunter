from parsers.demo_parser import find_best_tour


def check_tours():
    tour = find_best_tour()

    print("====== НАЙДЕН ТУР ======")
    print(f"Страна: {tour.country}")
    print(f"Город: {tour.city}")
    print(f"Отель: {tour.hotel}")
    print(f"Цена: {tour.price} ₽")

    return tour
from browser.browser import open_site
from parsers.demo_parser import find_best_tour


def check_tours():

    print("Запускаю браузер...")

    open_site()

    tour = find_best_tour()

    print(f"{tour.hotel} {tour.price}")

    return tour
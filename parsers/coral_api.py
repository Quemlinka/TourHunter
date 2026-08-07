import requests

from models.tour import Tour


class CoralAPI:

    ENCRYPT_URL = "https://www.coral.ru/endpoints/PackageTourHotelProduct/PriceSearchEncrypt"
    LIST_URL = "https://www.coral.ru/endpoints/PackageTourHotelProduct/PriceSearchList"

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update(
            {
                "accept": "application/json, text/plain, */*",
                "content-type": "application/json",
                "languagecode": "ru-RU",
                "currencycode": "RUB",
                "mobiletype": "Web",
                "origin": "https://www.coral.ru",
                "referer": "https://www.coral.ru/",
                "user-agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/150.0 Safari/537.36"
                ),
            }
        )

    def _encrypt(self):

        body = {
            "beginDates": [
                "2026-08-25T00:00:00Z",
                "2026-09-10T00:00:00Z"
            ],
            "arrivalLocations": [
                {
                    "id": "744-3-41-0",
                    "type": 3,
                    "name": "Нячанг (Nha Trang)"
                }
            ],
            "departureLocations": [
                {
                    "id": "2671-5",
                    "name": "Москва",
                    "type": 5
                }
            ],
            "nights": [
                {"value": 5},
                {"value": 6},
                {"value": 7},
                {"value": 10},
                {"value": 11},
                {"value": 12},
                {"value": 13},
                {"value": 14},
            ],
            "datePickerMode": 1,
            "roomCriterias": [
                {
                    "passengers": [
                        {
                            "age": 20,
                            "type": "adult"
                        }
                    ]
                }
            ],
            "reservationType": 1,
            "paging": {
                "pageNumber": 1,
                "pageSize": 100,
                "sortType": 0
            },
            "additionalFilters": [],
            "imageSizes": [0],
            "flightType": None,
        }

        r = self.session.post(self.ENCRYPT_URL, json=body)
        r.raise_for_status()

        return r.json()["result"]["queryParams"]["qp"]
    def get_tours(self):

        qp = self._encrypt()

        # Первый запрос (Coral подготавливает поиск)
        self.session.post(
        self.LIST_URL,
        json={
            "queryParam": qp,
            "notIncludeFilters": False,
            "searchSource": 0,
            "getOnlyTopHotels": True,
            "dontSearchTopHotels": False,
        },
    )
        # Второй запрос (возвращает products)
        r = self.session.post(
        self.LIST_URL,
        json={
            "queryParam": qp,
            "notIncludeFilters": True,
            "searchSource": 0,
            "getOnlyTopHotels": False,
            "dontSearchTopHotels": True,
        },
    )

        r.raise_for_status()

        data = r.json()

        result = data.get("result", {})

        products = result.get("products", [])

        tours = []

        for product in products:

            hotel = product.get("hotel", {})

            hotel_name = hotel.get("name", "")

            hotel_id = hotel.get("id", 0)
 
            offers = product.get("offers", [])

            for offer in offers:

                price = (
                    offer.get("price", {})
                    .get("amount")
                )

                if not price:
                    continue

                tours.append(
                    Tour(
                        id=str(offer.get("id", "")),
                        price=int(price),
                        checkin_date=offer.get("checkInDate", "")[:10],
                        tour_nights=int(
                            offer.get("stayNights", 0)
                        ),
                        hotel_nights=max(
                            int(offer.get("stayNights", 0)) - 1,
                            0,
                        ),
                        hotel=hotel_id,
                        resort=417,
                        operator=226,
                        room=hotel_name,
                        transfer="included",
                    )
                )

        return tours
    def get_best_tour(self):

        tours = self.get_tours()

        if not tours:
            return None

        return min(
            tours,
            key=lambda t: t.price,
        )
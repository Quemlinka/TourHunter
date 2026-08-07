"""
Настройки поиска TourHunter
"""

# Маршрут
DEPARTURE_CITY = 2          # Москва
COUNTRY = 22                # Вьетнам
RESORTS = (417,)            # Нячанг

# Диапазон дат вылета
DATE_FROM = "2026-08-25"
DATE_TO = "2026-09-10"

# Туристы
ADULTS = 1
CHILDREN = 0
INFANTS = 0

# Диапазон ночей
NIGHTS_FROM = 1
NIGHTS_TO = 20

# Максимальная цена для уведомлений
PRICE_LIMIT = 80_000

# Проверять каждые 5 минут
CHECK_INTERVAL_SECONDS = 300

# Таймаут HTTP-запросов
REQUEST_TIMEOUT_SECONDS = 30

# Сколько туров запрашивать у Travelata
RESULT_LIMIT = 20_000
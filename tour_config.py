"""Tour search settings, deliberately separate from Telegram credentials."""

# Travelata identifiers: Moscow, Vietnam, Nha Trang.
DEPARTURE_CITY = 2
COUNTRY = 22
RESORTS = (417,)

DATE_FROM = "2026-08-25"
DATE_TO = "2026-09-10"

ADULTS = 1
CHILDREN = 0
INFANTS = 0
NIGHTS_FROM = 7
NIGHTS_TO = 20

# A price ceiling for Telegram alerts. Searches still show the cheapest tour
# even if it exceeds this amount.
PRICE_LIMIT = 80_000

# Monitoring interval in seconds.
CHECK_INTERVAL_SECONDS = 300
REQUEST_TIMEOUT_SECONDS = 30
RESULT_LIMIT = 20_00
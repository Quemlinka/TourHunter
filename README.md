# TourHunter

Telegram bot that searches Travelata offers and monitors the lowest configured price.

## Start

1. Copy `.env.example` to `.env` and set `BOT_TOKEN` and `CHAT_ID`.
2. Adjust dates, travellers, nights and alert budget in `tour_config.py`.
3. Install dependencies: `python -m pip install -r requirements.txt`.
4. Run: `python main.py`.

The first scheduled check saves a baseline and does not notify. Later checks notify only when a cheaper offer (or a new equally cheap offer) is found within `PRICE_LIMIT`.

`data/last_tour.json` is generated automatically and must not be edited by hand.

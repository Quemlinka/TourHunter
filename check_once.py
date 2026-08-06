"""One price check for GitHub Actions.

Unlike main.py, this script starts, checks once, optionally sends a message,
and exits. That makes it suitable for a scheduled cloud job.
"""

from __future__ import annotations

import logging

import requests

from config import BOT_TOKEN, CHAT_ID, validate_bot_config
from models.tour import Tour
from services.price_watcher import CheckResult, PriceWatcher


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    validate_bot_config()

    result = PriceWatcher().check_prices()
    if result.tour is None:
        logging.warning("No matching tours were found.")
        return
    if not result.should_notify:
        logging.info("No notification is needed.")
        return

    _send_telegram_message(result)
    logging.info("Price alert sent.")


def _send_telegram_message(result: CheckResult) -> None:
    tour = result.tour
    assert tour is not None
    previous = result.previous_tour
    text = _format_alert(tour, previous)
    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": text},
        timeout=30,
    )
    response.raise_for_status()
    if not response.json().get("ok"):
        raise RuntimeError("Telegram did not accept the price alert.")


def _format_alert(tour: Tour, previous: Tour | None) -> str:
    change = ""
    if previous and previous.price != tour.price:
        difference = previous.price - tour.price
        if difference > 0:
            change = f"\n📉 Стало дешевле на: {_money(difference)}"
    room = f"\n🛏 Номер: {tour.room}" if tour.room else ""
    return (
        "🔥 Найден более выгодный тур!\n\n"
        "✈️ Москва → Нячанг\n"
        f"📅 Вылет: {tour.checkin_date}\n"
        f"🌙 Ночей: {tour.tour_nights}\n"
        f"💰 Цена: {_money(tour.price)}"
        f"{change}{room}"
    )


def _money(value: int) -> str:
    return f"{value:,} ₽".replace(",", " ")


if __name__ == "__main__":
    main()

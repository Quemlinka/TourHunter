from __future__ import annotations

import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.buttons import main_menu
from services.price_watcher import CheckResult, PriceWatcher
from tour_config import (
    ADULTS,
    CHECK_INTERVAL_SECONDS,
    DATE_FROM,
    DATE_TO,
    NIGHTS_FROM,
    NIGHTS_TO,
    PRICE_LIMIT,
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(_welcome_text(), reply_markup=main_menu())


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    if query.data == "check":
        await query.edit_message_text("🔎 Проверяю варианты. Это может занять около минуты…")
        try:
            result = await asyncio.to_thread(PriceWatcher().check_prices)
            text = _tour_text(result.tour, result.previous_tour, title="🔎 Результат поиска")
        except Exception:
            logger.exception("Manual price check failed")
            text = "❌ Не удалось получить туры. Попробуйте ещё раз немного позже."
        await query.edit_message_text(text, reply_markup=main_menu())
    elif query.data == "settings":
        await query.edit_message_text(_settings_text(), reply_markup=main_menu())
    elif query.data == "status":
        await query.edit_message_text(
            f"🟢 TourHunter работает.\n\nАвтоматическая проверка: каждые {CHECK_INTERVAL_SECONDS // 60} мин.",
            reply_markup=main_menu(),
        )


async def monitor_prices(context: ContextTypes.DEFAULT_TYPE) -> None:
    """JobQueue task: send a notification only for a new attractive offer."""
    try:
        result = await asyncio.to_thread(PriceWatcher().check_prices)
        if not result.tour or not result.should_notify:
            return
        await context.bot.send_message(
            chat_id=context.application.bot_data["chat_id"],
            text=_tour_text(result.tour, result.previous_tour, title="🔥 Найден более выгодный тур"),
        )
    except Exception:
        logger.exception("Scheduled price check failed")


def _welcome_text() -> str:
    return "🔥 TourHunter\n\n" + _settings_text() + "\n\n🟢 Бот работает"


def _settings_text() -> str:
    return (
        "⚙️ Настройки поиска\n\n"
        "✈️ Москва → Нячанг\n"
        f"📅 Период: {DATE_FROM} — {DATE_TO}\n"
        f"👤 Туристов: {ADULTS}\n"
        f"🌙 Ночей: {NIGHTS_FROM}–{NIGHTS_TO}\n"
        f"🎯 Уведомлять до: {_money(PRICE_LIMIT)}"
    )


def _tour_text(tour, previous, title: str) -> str:
    if tour is None:
        return "❌ Подходящих туров по заданным параметрам не найдено."
    change = ""
    if previous and tour.price != previous.price:
        difference = previous.price - tour.price
        direction = "дешевле" if difference > 0 else "дороже"
        change = f"\n📈 Изменение: {_money(abs(difference))} {direction}"
    room = f"\n🛏 Номер: {tour.room}" if tour.room else ""
    transfer = f"\n🚐 Трансфер: {tour.transfer}" if tour.transfer else ""
    return (
        f"{title}\n\n"
        "✈️ Москва → Нячанг\n"
        f"📅 Вылет: {tour.checkin_date}\n"
        f"🌙 Ночей: {tour.tour_nights}\n"
        f"💰 Цена: {_money(tour.price)}"
        f"{change}{room}{transfer}"
    )


def _money(value: int) -> str:
    return f"{value:,} ₽".replace(",", " ")

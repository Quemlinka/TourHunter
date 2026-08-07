from __future__ import annotations

import asyncio
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.buttons import main_menu
from models.tour import Tour
from services.links import travelata_search_url
from services.price_watcher import PriceWatcher
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
        await update.message.reply_text(
            _welcome_text(),
            reply_markup=main_menu(),
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    query = update.callback_query

    if query is None:
        return

    await query.answer()

    if query.data == "check":

        await query.edit_message_text(
            "🔎 Ищу самые дешёвые туры...\nЭто может занять около минуты."
        )

        try:

            result = await asyncio.to_thread(
                PriceWatcher().check_prices
            )

            text = _tour_text(
                result.tour,
                result.previous_tour,
                "🔎 Лучший найденный тур",
            )

            markup = (
                _tour_actions(result.tour)
                if result.tour
                else main_menu()
            )

        except Exception:

            logger.exception("Ошибка ручной проверки")

            text = (
                "❌ Не удалось получить данные "
                "от Travelata."
            )

            markup = main_menu()

        await query.edit_message_text(
            text,
            reply_markup=markup,
        )

        return

    if query.data == "settings":

        await query.edit_message_text(
            _settings_text(),
            reply_markup=main_menu(),
        )

        return

    if query.data == "status":

        await query.edit_message_text(
            (
                "🟢 TourHunter работает\n\n"
                f"Проверка каждые "
                f"{CHECK_INTERVAL_SECONDS // 60} минут."
            ),
            reply_markup=main_menu(),
        )


async def monitor_prices(
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    logger.info("=" * 60)
    logger.info("Автоматическая проверка")

    try:

        result = await asyncio.to_thread(
            PriceWatcher().check_prices
        )

    except Exception:

        logger.exception(
            "Ошибка проверки цен"
        )

        return

    if result.tour is None:

        logger.info(
            "Туры не найдены"
        )

        return

    if not result.should_notify:

        logger.info(
            "Уведомление не требуется"
        )

        return

    logger.info(
        "Отправляю уведомление..."
    )

    try:

        await context.bot.send_message(
            chat_id=context.application.bot_data["chat_id"],
            text=_tour_text(
                result.tour,
                result.previous_tour,
                "🔥 Найден более выгодный тур",
            ),
            reply_markup=_tour_actions(
                result.tour
            ),
        )

        logger.info(
            "Сообщение успешно отправлено"
        )

    except Exception:

        logger.exception(
            "Ошибка отправки Telegram"
        )


def _welcome_text() -> str:

    return (
        "🔥 TourHunter\n\n"
        + _settings_text()
        + "\n\n🟢 Бот запущен"
    )


def _settings_text() -> str:

    return (
        "⚙ Настройки\n\n"
        "✈ Москва → Нячанг\n"
        f"📅 {DATE_FROM} — {DATE_TO}\n"
        f"👤 Туристов: {ADULTS}\n"
        f"🌙 Ночей: {NIGHTS_FROM}-{NIGHTS_TO}\n"
        f"💰 Лимит: {_money(PRICE_LIMIT)}"
    )


def _tour_text(
    tour,
    previous,
    title,
) -> str:

    if tour is None:

        return (
            "❌ Подходящих туров "
            "не найдено."
        )

    change = ""

    if previous:

        delta = previous.price - tour.price

        if delta > 0:

            change = (
                f"\n📉 Цена снизилась "
                f"на {_money(delta)}"
            )

        elif delta < 0:

            change = (
                f"\n📈 Цена выросла "
                f"на {_money(-delta)}"
            )

    return (
        f"{title}\n\n"
        "✈ Москва → Нячанг\n\n"
        f"📅 Вылет: {tour.checkin_date}\n"
        f"🌙 Ночей: {tour.tour_nights}\n"
        f"💰 Цена: {_money(tour.price)}"
        f"{change}"
    )


def _money(value: int) -> str:

    return f"{value:,} ₽".replace(",", " ")


def _tour_actions(
    tour: Tour | None,
) -> InlineKeyboardMarkup:

    rows = []

    if tour:

        rows.append([
            InlineKeyboardButton(
                "🌴 Открыть в Travelata",
                url=travelata_search_url(tour),
            )
        ])

    rows.extend(
        main_menu().inline_keyboard
    )

    return InlineKeyboardMarkup(rows)
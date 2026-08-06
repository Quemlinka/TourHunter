from telegram import Update
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler
)

from bot.buttons import main_menu


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        text=
        """
🔥 TourHunter

🌴 Направление:
Вьетнам → Нячанг

💰 Лимит:
80 000 ₽

📅 Даты:
25-31 августа

🟢 Статус:
Бот работает
        """,
        reply_markup=main_menu()
    )


async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()


    if query.data == "check":

        await query.edit_message_text(
            """
🔎 Проверка запущена...

Пока я еще учусь искать туры 😄

Скоро подключим настоящий поиск.
            """
        )


    elif query.data == "settings":

        await query.edit_message_text(
            """
⚙ Настройки

🌴 Нячанг
💰 До 80000 ₽
👤 1 человек

Скоро добавим изменение параметров.
            """
        )


    elif query.data == "status":

        await query.edit_message_text(
            """
📊 Статус

🟢 Бот работает

Версия:
TourHunter v0.2
            """
        )


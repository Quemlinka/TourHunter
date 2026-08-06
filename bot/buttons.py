from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu():

    keyboard = [
        [
            InlineKeyboardButton(
                "🔎 Проверить сейчас",
                callback_data="check"
            )
        ],
        [
            InlineKeyboardButton(
                "⚙ Настройки",
                callback_data="settings"
            )
        ],
        [
            InlineKeyboardButton(
                "📊 Статус",
                callback_data="status"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)
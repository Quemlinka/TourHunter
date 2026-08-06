from __future__ import annotations

import logging

from telegram.ext import Application, CallbackQueryHandler, CommandHandler

from bot.handlers import button_handler, monitor_prices, start
from config import BOT_TOKEN, CHAT_ID, validate_bot_config
from tour_config import CHECK_INTERVAL_SECONDS


def main() -> None:
    validate_bot_config()
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        level=logging.INFO,
    )

    app = Application.builder().token(BOT_TOKEN).build()
    app.bot_data["chat_id"] = CHAT_ID
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    if app.job_queue is None:
        raise RuntimeError("Install dependencies with: pip install -r requirements.txt")
    app.job_queue.run_repeating(monitor_prices, interval=CHECK_INTERVAL_SECONDS, first=10)

    logging.getLogger(__name__).info("TourHunter started")
    app.run_polling()


if __name__ == "__main__":
    main()

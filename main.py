from __future__ import annotations

import logging

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
)

from bot.handlers import (
    button_handler,
    monitor_prices,
    start,
)

from config import (
    BOT_TOKEN,
    CHAT_ID,
    validate_bot_config,
)

from tour_config import CHECK_INTERVAL_SECONDS


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)

logger = logging.getLogger(__name__)


def main() -> None:

    validate_bot_config()

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.bot_data["chat_id"] = CHAT_ID

    app.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )

    if app.job_queue is None:
        raise RuntimeError(
            "JobQueue недоступен."
        )

    app.job_queue.run_repeating(
        monitor_prices,
        interval=CHECK_INTERVAL_SECONDS,
        first=10,
    )

    logger.info("=" * 60)
    logger.info("TourHunter запущен")
    logger.info("CHAT_ID: %s", CHAT_ID)
    logger.info(
        "Проверка каждые %s секунд",
        CHECK_INTERVAL_SECONDS,
    )
    logger.info("=" * 60)

    app.run_polling(
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
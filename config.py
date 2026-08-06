"""Telegram settings. Keep credentials in .env, never in this file."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

_chat_id = os.getenv("CHAT_ID", "").strip()
CHAT_ID = int(_chat_id) if _chat_id else None


def validate_bot_config() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing. Add it to the .env file.")
    if CHAT_ID is None:
        raise RuntimeError("CHAT_ID is missing. Add it to the .env file.")

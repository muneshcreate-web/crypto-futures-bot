"""Telegram notifications"""

import requests
from datetime import datetime
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID


def send(message: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {message}")

    if not TELEGRAM_TOKEN or "DAALO" in TELEGRAM_TOKEN:
        return

    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML",
            },
            timeout=10,
        )
    except Exception as e:
        print(f"[Telegram error] {e}")

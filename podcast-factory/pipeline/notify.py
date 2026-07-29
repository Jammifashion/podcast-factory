"""Benachrichtigung per Telegram-Bot. Ohne Token wird still uebersprungen,
der Workflow laeuft trotzdem weiter (Notification ist Komfort, kein Muss)."""
from __future__ import annotations

import argparse
import os

import requests

MESSAGES = {
    "draft": (
        "🎙️ *{podcast}* – Script & Dialogue fertig.\n"
        "Bitte pruefen und im Production-Lock freigeben (oder ablehnen):\n{url}"
    ),
    "audio": (
        "✅ *{podcast}* – Audio gerendert.\n"
        "MP3 als Artefakt im Lauf, bitte final abhoeren vor Veroeffentlichung:\n{url}"
    ),
}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--stage", choices=MESSAGES.keys(), required=True)
    p.add_argument("--podcast", required=True)
    p.add_argument("--run-url", required=True)
    args = p.parse_args()

    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat:
        print("  Telegram uebersprungen (kein Token/Chat gesetzt)")
        return

    text = MESSAGES[args.stage].format(podcast=args.podcast, url=args.run_url)
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat, "text": text, "parse_mode": "Markdown"},
        timeout=30,
    )
    print("  Telegram-Status:", r.status_code)


if __name__ == "__main__":
    main()

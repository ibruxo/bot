from config import Config
from services.messengers.telegram import TelegramAdapter


def build_adapters():
    """
    Build enabled messenger adapters.

    This project is Telegram-only.
    """

    adapters = {}

    if not Config.BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing in .env")

    adapters["telegram"] = TelegramAdapter(token=Config.BOT_TOKEN)

    return adapters

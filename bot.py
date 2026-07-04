import time
import logging
import requests

from config import Config
from scheduler import MessageScheduler
from redis.client import get_redis
from services.verse_service import VerseService


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class BaleBot:

    def __init__(self):
        self.api_url = Config.get_bale_full_api_url()
        self.offset = 0

    # -------------------------
    # HTTP layer
    # -------------------------
    def _request(self, endpoint: str, **kwargs):
        url = f"{self.api_url}/{endpoint}"
        response = requests.post(url, **kwargs)
        return response.json()

    def get_updates(self) -> list:
        try:
            response = requests.get(
                f"{self.api_url}/getUpdates",
                params={"offset": self.offset, "timeout": 30},
                timeout=35
            )

            data = response.json()

            if data.get("ok"):
                return data.get("result", [])

            return []

        except Exception as e:
            logger.error(f"get_updates error: {e}")
            return []

    def send_message(self, chat_id: int, text: str,
                     reply_markup: dict = None,
                     parse_mode: str = None):

        payload = {
            "chat_id": chat_id,
            "text": text
        }

        if reply_markup:
            payload["reply_markup"] = reply_markup

        if parse_mode:
            payload["parse_mode"] = parse_mode

        return self._request("sendMessage", json=payload)

    # -------------------------
    # Verse layer (clean)
    # -------------------------
    def send_verse(self, chat_id: int, verse_service: VerseService):
        verse = verse_service.get_random_verse()
        message = verse_service.format_verse(verse, Config)

        return self.send_message(
            chat_id,
            message,
            parse_mode="Markdown"
        )

    # -------------------------
    # UI helpers
    # -------------------------
    def send_keyboard(self, chat_id: int, text: str):
        reply_markup = {
            "keyboard": [
                [{"text": "📖 ارسال آیه تصادفی"}],
                [{"text": "📚 راهنمای اضافه کردن به کانال"}]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": False
        }

        return self.send_message(chat_id, text, reply_markup)

    # -------------------------
    # Update processing
    # -------------------------
    def process_updates(self, updates: list, verse_service: VerseService):

        for update in updates:
            self.offset = update["update_id"] + 1

            if "message" not in update:
                continue

            message = update["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")

            if text in ["/start", "شروع"]:
                self._handle_start(chat_id)

            elif text in ["/random", "آیه تصادفی", "📖 ارسال آیه تصادفی"]:
                self._handle_random(chat_id, verse_service)

            elif text in ["/help", "راهنما", "📚 راهنمای اضافه کردن به کانال"]:
                self._handle_help(chat_id)

            elif text in ["/schedule", "زمان"]:
                self._handle_schedule(chat_id)

    # -------------------------
    # Handlers
    # -------------------------
    def _handle_start(self, chat_id: int):
        text = (
            "🤖 *بازو قرآن ناطق*\n\n"
            "سلام! به بازو قرآن ناطق خوش اومدین.\n\n"
            "📚 ارسال آیات تصادفی قرآن به همراه ترجمه.\n\n"
            "برای شروع، روی دکمه زیر کلیک کن."
        )

        self.send_keyboard(chat_id, text)

    def _handle_random(self, chat_id: int, verse_service: VerseService):
        try:
            self.send_verse(chat_id, verse_service)
            logger.info(f"sent verse -> chat_id: {chat_id}")

        except Exception as e:
            logger.error(f"random verse error: {e}")
            self.send_message(chat_id, "Error occurred!")

    def _handle_help(self, chat_id: int):
        text = (
            "📖 *راهنما*\n\n"
            "• /random → آیه تصادفی\n"
            "• /schedule → زمان ارسال خودکار\n"
        )

        self.send_message(chat_id, text)

    def _handle_schedule(self, chat_id: int):
        text = (
            "⏰ *زمان ارسال*\n\n"
            f"📢 عمومی: {Config.SCHEDULE_PUBLIC_HOUR:02d}:{Config.SCHEDULE_PUBLIC_MINUTE:02d}\n"
            f"👤 کاربران: {Config.SCHEDULE_USER_HOUR:02d}:{Config.SCHEDULE_USER_MINUTE:02d}\n"
        )

        self.send_message(chat_id, text)


# -------------------------
# MAIN ENTRY
# -------------------------
def main():
    print("=" * 60)
    print("🤖 Natiq Bot Starting")
    print("=" * 60)

    redis = get_redis()
    verse_service = VerseService(redis)

    bot = BaleBot()

    scheduler = MessageScheduler(bot, verse_service)
    scheduler.start()

    print("Bot is running...")

    while True:
        try:
            updates = bot.get_updates()

            if updates:
                bot.process_updates(updates, verse_service)

        except KeyboardInterrupt:
            print("Stopping bot...")
            scheduler.stop()
            break

        except Exception as e:
            logger.error(f"main loop error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()

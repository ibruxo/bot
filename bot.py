import logging
import time

from cache.client import get_redis
from cache.rate_limiter import RateLimiter
from cache.verse_cache import VerseCache
from config import Config
from scheduler import MessageScheduler
from services import user_service
from services.messengers.base import NormalizedMessage
from services.messengers.registry import build_adapters
from services.quran_api_client import QuranApiClient
from services.verse_ingestion_service import VerseIngestionService
from services.verse_service import VerseService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


class BotRunner:
    """
    Polls every platform adapter that supports polling (Bale, Telegram,
    Rubika) and dispatches commands. Platform-specific HTTP details live
    in services/messengers/*; this class only knows the normalized
    message shape, so command handling is identical across platforms.

    Note: Eitaa has no inbound-updates mechanism (see
    services/messengers/eitaa.py), so it only ever receives scheduled
    broadcasts, never replies to commands.
    """

    def __init__(self, verse_service: VerseService, rate_limiter: RateLimiter):
        self.adapters = build_adapters()
        self.verse_service = verse_service
        self.rate_limiter = rate_limiter

    def run_forever(self):
        polling_adapters = {p: a for p, a in self.adapters.items() if a.supports_polling}

        if not polling_adapters:
            logger.warning("No platforms support polling — the process will idle (scheduler still runs)")

        while True:
            try:
                for platform, adapter in polling_adapters.items():
                    messages = adapter.get_updates()
                    if messages:
                        self._process_messages(adapter, messages)

                time.sleep(1)

            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.error(f"main loop error: {e}")
                time.sleep(5)

    # -------------------------
    # Update processing
    # -------------------------
    def _process_messages(self, adapter, messages: list[NormalizedMessage]):
        for message in messages:
            try:
                user_service.register_incoming_message(
                    message.platform,
                    {
                        "id": message.chat_id,
                        "type": message.chat_type,
                        "username": message.username,
                        "first_name": message.first_name,
                        "title": message.title,
                    },
                )
            except Exception as e:
                logger.error(f"failed to register {message.platform}:{message.chat_id}: {e}")

            text = message.text

            if text in ["/start", "شروع"]:
                self._handle_start(adapter, message)
            elif text in ["/random", "آیه تصادفی", "📖 ارسال آیه تصادفی"]:
                self._handle_random(adapter, message)
            elif text in ["/help", "راهنما", "📚 راهنمای اضافه کردن به کانال"]:
                self._handle_help(adapter, message)
            elif text in ["/schedule", "زمان"]:
                self._handle_schedule(adapter, message)
            elif text == "/stats":
                self._handle_stats(adapter, message)

    # -------------------------
    # Handlers
    # -------------------------
    def _handle_start(self, adapter, message: NormalizedMessage):
        text = (
            "🤖 *بازو قرآن ناطق*\n\n"
            "سلام! به بازو قرآن ناطق خوش اومدین.\n\n"
            "📚 ارسال آیات تصادفی قرآن به همراه ترجمه.\n\n"
            "برای آیه تصادفی /random رو بفرست."
        )
        adapter.send_message(message.chat_id, text)

    def _handle_random(self, adapter, message: NormalizedMessage):
        rate_key = f"{message.platform}:{message.chat_id}"

        if not self.rate_limiter.allow(rate_key):
            wait = self.rate_limiter.remaining_seconds(rate_key)
            adapter.send_message(message.chat_id, f"⏳ لطفاً {wait} ثانیه دیگر دوباره امتحان کنید.")
            return

        try:
            verse = self.verse_service.get_random_verse()

            if not verse:
                adapter.send_message(message.chat_id, "آیه‌ای در دسترس نیست، لطفاً بعداً امتحان کنید.")
                return

            text = self.verse_service.format_verse(verse)
            adapter.send_message(message.chat_id, text, parse_mode="Markdown")
            logger.info(f"sent verse -> {message.platform}:{message.chat_id}")

        except Exception as e:
            logger.error(f"random verse error: {e}")
            adapter.send_message(message.chat_id, "خطایی رخ داد!")

    def _handle_help(self, adapter, message: NormalizedMessage):
        text = (
            "📖 *راهنما*\n\n"
            "• /random → آیه تصادفی\n"
            "• /schedule → زمان ارسال خودکار\n"
        )
        adapter.send_message(message.chat_id, text)

    def _handle_schedule(self, adapter, message: NormalizedMessage):
        text = (
            "⏰ *زمان ارسال*\n\n"
            f"📢 عمومی: {Config.SCHEDULE_PUBLIC_HOUR:02d}:{Config.SCHEDULE_PUBLIC_MINUTE:02d}\n"
            f"👤 کاربران: {Config.SCHEDULE_USER_HOUR:02d}:{Config.SCHEDULE_USER_MINUTE:02d}\n"
        )
        adapter.send_message(message.chat_id, text)

    def _handle_stats(self, adapter, message: NormalizedMessage):
        if not user_service.is_admin(message.platform, message.chat_id):
            return  # silently ignore for non-admins

        stats = user_service.get_stats()
        last_ingestion = stats.get("last_verse_ingestion") or {}

        text = (
            "📊 *آمار*\n\n"
            f"👤 کاربران: {stats['users']}\n"
            f"👥 گروه‌ها: {stats['groups']}\n"
            f"📢 کانال‌ها: {stats['channels']}\n"
            f"🔄 آخرین به‌روزرسانی آیات: "
            f"{last_ingestion.get('count', '—')} آیه در {last_ingestion.get('at', 'نامشخص')}\n"
        )
        adapter.send_message(message.chat_id, text)


# -------------------------
# MAIN ENTRY
# -------------------------
def main():
    print("=" * 60)
    print("🤖 Natiq Bot Starting")
    print("=" * 60)

    redis_client = get_redis()
    verse_cache = VerseCache(redis_client)
    verse_service = VerseService(verse_cache)
    rate_limiter = RateLimiter(
        redis_client,
        max_requests=Config.RATE_LIMIT_MAX_REQUESTS,
        window_seconds=Config.RATE_LIMIT_WINDOW_SECONDS,
    )

    api_client = QuranApiClient()
    ingestion_service = VerseIngestionService(api_client, verse_cache)

    # One-time startup bootstrapping.
    user_service.bootstrap_admins()
    user_service.seed_static_recipients()

    if Config.INGEST_ON_STARTUP:
        try:
            ingestion_service.ensure_data_available()
        except Exception as e:
            logger.error(f"Startup verse ingestion failed: {e}")

    runner = BotRunner(verse_service, rate_limiter)

    if not runner.adapters:
        logger.error(
            "No messenger platforms are configured (check ENABLED_PLATFORMS and "
            "the matching *_BOT_TOKEN in .env). Exiting."
        )
        return

    scheduler = MessageScheduler(runner.adapters, verse_service, ingestion_service)
    scheduler.start()

    print(f"Bot is running on: {', '.join(runner.adapters.keys())}")

    try:
        runner.run_forever()
    except KeyboardInterrupt:
        print("Stopping bot...")
        scheduler.stop()


if __name__ == "__main__":
    main()

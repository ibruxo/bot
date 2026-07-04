import logging
from typing import List

from db.repositories import sent_message_repo
from db.session import get_session
from services.verse_service import VerseService

logger = logging.getLogger(__name__)


class BroadcastService:
    """
    Sends a verse to a list of chats and records the outcome in
    `sent_messages`. Used by the scheduler for both the public
    (channels + groups) and per-user daily broadcasts, so that logic
    isn't duplicated (as it was in the old scheduler.py).
    """

    def __init__(self, bot, verse_service: VerseService):
        self.bot = bot
        self.verse_service = verse_service

    def send_to_many(self, chat_ids: List[int], chat_type: str) -> tuple[int, int]:
        success = 0
        failed = 0

        for chat_id in chat_ids:
            verse = self.verse_service.get_random_verse()

            if not verse:
                logger.error("No verse available to send — is the cache/DB empty?")
                failed += 1
                continue

            message = self.verse_service.format_verse(verse)

            try:
                self.bot.send_message(chat_id, message, parse_mode="Markdown")

                with get_session() as session:
                    sent_message_repo.log(
                        session,
                        chat_id=chat_id,
                        chat_type=chat_type,
                        verse_id=verse.get("id"),
                        message_text=message,
                        success=True,
                    )

                success += 1
                logger.info(
                    f"✅ Sent to {chat_id} ({chat_type}): "
                    f"{verse.get('surah_name')} {verse.get('verse_number')}"
                )

            except Exception as e:
                failed += 1
                logger.error(f"❌ Failed for {chat_id} ({chat_type}): {e}")

                with get_session() as session:
                    sent_message_repo.log(
                        session,
                        chat_id=chat_id,
                        chat_type=chat_type,
                        verse_id=verse.get("id"),
                        message_text=message,
                        success=False,
                        error=str(e),
                    )

        return success, failed

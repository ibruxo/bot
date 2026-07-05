import logging
from typing import Dict, List, Tuple

from db.repositories import sent_message_repo
from db.session import get_session
from services.messengers.base import MessengerAdapter
from services.verse_service import VerseService

logger = logging.getLogger(__name__)


class BroadcastService:
    """
    Sends a verse to a list of (platform, chat_id) recipients and records
    the outcome in `sent_messages`. Used by the scheduler for both the
    public (channels + groups) and per-user daily broadcasts across every
    configured platform.
    """

    def __init__(self, adapters: Dict[str, MessengerAdapter], verse_service: VerseService):
        self.adapters = adapters
        self.verse_service = verse_service

    def send_to_many(self, recipients: List[Tuple[str, str]], chat_type: str) -> tuple[int, int]:
        """`recipients` is a list of (platform, chat_id) tuples."""
        success = 0
        failed = 0

        for platform, chat_id in recipients:
            adapter = self.adapters.get(platform)

            if not adapter:
                logger.warning(f"No adapter configured for platform '{platform}' — skipping {chat_id}")
                failed += 1
                continue

            verse = self.verse_service.get_random_verse()

            if not verse:
                logger.error("No verse available to send — is the cache/DB empty?")
                failed += 1
                continue

            message = self.verse_service.format_verse(verse)
            ok = adapter.send_message(chat_id, message, parse_mode="Markdown")

            with get_session() as session:
                sent_message_repo.log(
                    session,
                    platform=platform,
                    chat_id=chat_id,
                    chat_type=chat_type,
                    verse_id=verse.get("id"),
                    message_text=message,
                    success=ok,
                    error=None if ok else "send_message returned failure",
                )

            if ok:
                success += 1
                logger.info(
                    f"✅ Sent to {platform}:{chat_id} ({chat_type}): "
                    f"{verse.get('surah_name')} {verse.get('verse_number')}"
                )
            else:
                failed += 1
                logger.error(f"❌ Failed for {platform}:{chat_id} ({chat_type})")

        return success, failed

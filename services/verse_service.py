import logging
from typing import Any, Dict, Optional

from cache.verse_cache import VerseCache
from db.repositories import verse_repo
from db.session import get_session

logger = logging.getLogger(__name__)

PERIOD_ICONS = {
    "makki": "🕋",
    "madani": "🕌",
}
DEFAULT_ICON = "📖"


class VerseService:
    """
    The single place the bot goes to get "a verse to send".

    Tries the fast path (Redis cache) first, and falls back to a direct
    Postgres query if the cache is empty (e.g. right after a restart,
    before the scheduled refresh has run).
    """

    def __init__(self, verse_cache: VerseCache):
        self.verse_cache = verse_cache

    def get_random_verse(self) -> Optional[Dict[str, Any]]:
        verse = self.verse_cache.get_random_verse()
        if verse:
            return verse

        logger.warning("Verse cache empty — falling back to Postgres")

        with get_session() as session:
            db_verse = verse_repo.get_random(session)
            if not db_verse:
                return None

            return {
                "id": db_verse.id,
                "surah_name": db_verse.surah_name,
                "surah_number": db_verse.surah_number,
                "verse_number": db_verse.verse_number,
                "verse_text": db_verse.verse_text,
                "translation": db_verse.translation,
                "period": db_verse.period or "",
            }

    @staticmethod
    def format_verse(verse: Dict[str, Any]) -> str:
        surah_name = verse.get("surah_name") or "نامشخص"
        verse_number = verse.get("verse_number", 0)
        verse_text = verse.get("verse_text", "")
        translation = verse.get("translation", "")
        period = verse.get("period", "")

        icon = PERIOD_ICONS.get(period, DEFAULT_ICON)

        return (
            f"{icon} *سوره {surah_name}*\n\n"
            f"📖 *{verse_text} ﴿{verse_number}﴾*\n\n"
            f"📝 {translation}\n"
        )

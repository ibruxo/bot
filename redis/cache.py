import json
import random
from typing import Dict, List, Any, Optional

from redis import Redis


class CacheManager:
    """
    Redis-based cache manager for verses.

    Responsibilities:
    - Load verses into Redis
    - Fetch random verse
    - Format verse (presentation logic)
    """

    VERSE_LIST_KEY = "verses:all"

    def __init__(self, redis: Redis):
        self.redis = redis
        self.is_loaded = False

    # -----------------------------
    # LOADING
    # -----------------------------
    def load_verses(self, verses: List[Dict[str, Any]]) -> None:
        """
        Load verses into Redis (bulk replace).
        """

        pipe = self.redis.pipeline()
        pipe.delete(self.VERSE_LIST_KEY)

        for verse in verses:
            pipe.rpush(self.VERSE_LIST_KEY, json.dumps(verse))

        pipe.execute()
        self.is_loaded = True

    # -----------------------------
    # FETCHING
    # -----------------------------
    def get_random_verse(self) -> Dict[str, Any]:
        """
        Get a random verse from Redis.
        """

        size = self.redis.llen(self.VERSE_LIST_KEY)

        if size == 0:
            raise ValueError("Redis verse cache is empty")

        index = random.randint(0, size - 1)

        raw = self.redis.lindex(self.VERSE_LIST_KEY, index)

        if not raw:
            raise ValueError("Failed to fetch verse from Redis")

        return json.loads(raw)

    # -----------------------------
    # FORMATTING (kept here intentionally)
    # -----------------------------
    def format_verse(self, verse: Dict[str, Any]) -> str:
        """
        Format verse for Telegram message.
        """

        surah_name = verse.get("surah_name", "نامشخص")
        verse_number = verse.get("verse_number", 0)
        verse_text = verse.get("verse_text", "")
        translation = verse.get("translation", "")
        period = verse.get("period", "")

        if period == "makki":
            icon = "🕋"
        elif period == "madani":
            icon = "🕌"
        else:
            icon = "📖"

        return (
            f"{icon} *سوره {surah_name}*\n\n"
            f"📖 *{verse_text} ﴿{verse_number}﴾*\n\n"
            f"📝 {translation}\n"
        )

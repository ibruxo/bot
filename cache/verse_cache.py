import json
import random
from typing import Any, Dict, List, Optional

from redis import Redis


class VerseCache:
    """
    Thin Redis cache in front of Postgres verse data.

    Postgres is the source of truth (see db/models/verse.py +
    db/repositories/verse_repo.py). This class never invents data on its
    own; `refresh()` must be called (by the ingestion service) to load
    verses from Postgres into Redis.
    """

    VERSE_LIST_KEY = "verses:all"

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def refresh(self, verses: List[Dict[str, Any]]) -> int:
        """Replace the cached verse list with the given verses (from Postgres)."""
        pipe = self.redis.pipeline()
        pipe.delete(self.VERSE_LIST_KEY)

        for verse in verses:
            pipe.rpush(self.VERSE_LIST_KEY, json.dumps(verse))

        pipe.execute()
        return len(verses)

    def size(self) -> int:
        return self.redis.llen(self.VERSE_LIST_KEY)

    def get_random_verse(self) -> Optional[Dict[str, Any]]:
        size = self.size()

        if size == 0:
            return None

        index = random.randint(0, size - 1)
        raw = self.redis.lindex(self.VERSE_LIST_KEY, index)

        return json.loads(raw) if raw else None

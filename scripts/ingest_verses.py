"""
Standalone script to (re)ingest verses from the Natiq API into Postgres
and refresh the Redis cache. Useful for a first-time setup, or as a cron
job independent of the bot process.

Usage:
    python -m scripts.ingest_verses
"""

import logging

from cache.client import get_redis
from cache.verse_cache import VerseCache
from services.quran_api_client import QuranApiClient
from services.verse_ingestion_service import VerseIngestionService

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main():
    redis_client = get_redis()
    verse_cache = VerseCache(redis_client)
    api_client = QuranApiClient()

    service = VerseIngestionService(api_client, verse_cache)
    count = service.run()

    print(f"Ingested {count} verses.")


if __name__ == "__main__":
    main()

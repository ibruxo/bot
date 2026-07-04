import logging
from datetime import datetime, timezone

from config import Config
from cache.verse_cache import VerseCache
from db.repositories import bot_state_repo, verse_repo
from db.session import get_session
from services.quran_api_client import QuranApiClient

LAST_INGESTION_STATE_KEY = "last_verse_ingestion"

logger = logging.getLogger(__name__)


class VerseIngestionService:
    """
    Pulls verses from the Natiq Quran API into Postgres (source of truth),
    then refreshes the Redis cache from Postgres.

    This replaces the old project's two disconnected, half-built verse
    systems with a single real pipeline: API -> Postgres -> Redis.
    """

    def __init__(self, api_client: QuranApiClient, verse_cache: VerseCache):
        self.api_client = api_client
        self.verse_cache = verse_cache

    def run(self, mushaf: str | None = None, translator_uuid: str | None = None) -> int:
        mushaf = mushaf or Config.MUSHAF
        translator_uuid = translator_uuid or Config.TRANSLATOR_UUID

        logger.info(f"📥 Fetching verses from Natiq API (mushaf={mushaf})")
        verses = self.api_client.fetch_all_verses(mushaf, translator_uuid)

        if not verses:
            logger.warning("Natiq API returned no verses — nothing to ingest")
            return 0

        with get_session() as session:
            verse_repo.bulk_upsert(session, verses)
            bot_state_repo.set(
                session,
                LAST_INGESTION_STATE_KEY,
                {
                    "at": datetime.now(timezone.utc).isoformat(),
                    "count": len(verses),
                    "mushaf": mushaf,
                },
            )

        self.refresh_cache(mushaf)

        logger.info(f"✅ Ingested {len(verses)} verse(s) into Postgres")
        return len(verses)

    def refresh_cache(self, mushaf: str | None = None) -> int:
        mushaf = mushaf or Config.MUSHAF

        with get_session() as session:
            verses = verse_repo.list_all_as_dicts(session, mushaf=mushaf)

        count = self.verse_cache.refresh(verses)
        logger.info(f"🔄 Redis verse cache refreshed with {count} verse(s)")
        return count

    def ensure_data_available(self) -> None:
        """Called on startup: ingest if Postgres has no verses yet, and
        make sure the Redis cache is warm either way."""
        with get_session() as session:
            existing = verse_repo.count(session)

        if existing == 0:
            logger.info("No verses in Postgres yet — running initial ingestion")
            self.run()
        else:
            self.refresh_cache()

import logging
from typing import Dict

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from config import Config
from db.repositories import channel_repo, group_repo, user_repo
from db.session import get_session
from services.broadcast_service import BroadcastService
from services.messengers.base import MessengerAdapter
from services.verse_ingestion_service import VerseIngestionService
from services.verse_service import VerseService

logger = logging.getLogger(__name__)


class MessageScheduler:
    def __init__(
        self,
        adapters: Dict[str, MessengerAdapter],
        verse_service: VerseService,
        ingestion_service: VerseIngestionService,
    ):
        self.verse_service = verse_service
        self.ingestion_service = ingestion_service
        self.broadcast = BroadcastService(adapters, verse_service)

        self.scheduler = BackgroundScheduler(
            timezone=Config.SCHEDULE_TIMEZONE,
            job_defaults={
                "coalesce": True,
                "max_instances": 1,
                "misfire_grace_time": 60,
            },
        )

    # -----------------------------
    # Jobs
    # -----------------------------
    def _send_to_public(self):
        with get_session() as session:
            recipients = channel_repo.list_active(session) + group_repo.list_active(session)

        if not recipients:
            logger.warning("No channels or groups registered yet")
            return

        logger.info(f"📢 Sending to public targets: {len(recipients)}")
        success, failed = self.broadcast.send_to_many(recipients, chat_type="public")
        logger.info(f"📊 Public send complete | success={success} failed={failed}")

    def _send_to_users(self):
        with get_session() as session:
            recipients = user_repo.list_active(session)

        if not recipients:
            logger.warning("No users registered yet")
            return

        logger.info(f"📢 Sending to users: {len(recipients)}")
        success, failed = self.broadcast.send_to_many(recipients, chat_type="user")
        logger.info(f"📊 User send complete | success={success} failed={failed}")

    def _refresh_verse_cache(self):
        try:
            self.ingestion_service.run()
        except Exception as e:
            logger.error(f"Verse refresh job failed: {e}")

    # -----------------------------
    # Lifecycle
    # -----------------------------
    def start(self):
        self.scheduler.add_job(
            func=self._send_to_public,
            trigger=CronTrigger(
                hour=Config.SCHEDULE_PUBLIC_HOUR,
                minute=Config.SCHEDULE_PUBLIC_MINUTE,
                timezone=Config.SCHEDULE_TIMEZONE,
            ),
            id="daily_public_verse",
            replace_existing=True,
        )

        self.scheduler.add_job(
            func=self._send_to_users,
            trigger=CronTrigger(
                hour=Config.SCHEDULE_USER_HOUR,
                minute=Config.SCHEDULE_USER_MINUTE,
                timezone=Config.SCHEDULE_TIMEZONE,
            ),
            id="daily_user_verse",
            replace_existing=True,
        )

        self.scheduler.add_job(
            func=self._refresh_verse_cache,
            trigger="interval",
            hours=Config.VERSE_REFRESH_INTERVAL_HOURS,
            id="verse_refresh",
            replace_existing=True,
        )

        self.scheduler.start()

        logger.info("=" * 50)
        logger.info("⏰ Scheduler started successfully")
        logger.info(f"📢 Public: {Config.SCHEDULE_PUBLIC_HOUR:02d}:{Config.SCHEDULE_PUBLIC_MINUTE:02d}")
        logger.info(f"👤 Users:  {Config.SCHEDULE_USER_HOUR:02d}:{Config.SCHEDULE_USER_MINUTE:02d}")
        logger.info(f"🔄 Verse refresh every {Config.VERSE_REFRESH_INTERVAL_HOURS}h")
        logger.info("=" * 50)

    def stop(self):
        self.scheduler.shutdown(wait=False)
        logger.info("⛔ Scheduler stopped")

    def get_next_run(self, job_id: str = "daily_public_verse"):
        job = self.scheduler.get_job(job_id)
        return job.next_run_time if job else None

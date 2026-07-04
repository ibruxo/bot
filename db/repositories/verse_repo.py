from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from db.models.verse import Verse


def bulk_upsert(session: Session, verses: List[Dict[str, Any]]) -> int:
    """
    Insert new verses / update existing ones (matched by mushaf +
    translator_uuid + surah_number + verse_number) in one statement.

    Each dict in `verses` must contain the columns of Verse (see
    services/quran_api_client.py for the normalized shape).
    """
    if not verses:
        return 0

    stmt = pg_insert(Verse).values(verses)

    update_cols = {
        "external_id": stmt.excluded.external_id,
        "surah_name": stmt.excluded.surah_name,
        "verse_text": stmt.excluded.verse_text,
        "translation": stmt.excluded.translation,
        "period": stmt.excluded.period,
        "updated_at": func.now(),
    }

    stmt = stmt.on_conflict_do_update(
        constraint="uq_verse_identity",
        set_=update_cols,
    )

    session.execute(stmt)
    return len(verses)


def get_random(session: Session, mushaf: Optional[str] = None) -> Optional[Verse]:
    stmt = select(Verse)
    if mushaf:
        stmt = stmt.where(Verse.mushaf == mushaf)
    stmt = stmt.order_by(func.random()).limit(1)
    return session.scalar(stmt)


def list_all_as_dicts(session: Session, mushaf: Optional[str] = None) -> List[Dict[str, Any]]:
    """Used to (re)populate the Redis cache from Postgres."""
    stmt = select(Verse)
    if mushaf:
        stmt = stmt.where(Verse.mushaf == mushaf)

    rows = session.scalars(stmt).all()

    return [
        {
            "id": v.id,
            "surah_name": v.surah_name,
            "surah_number": v.surah_number,
            "verse_number": v.verse_number,
            "verse_text": v.verse_text,
            "translation": v.translation,
            "period": v.period or "",
        }
        for v in rows
    ]


def count(session: Session) -> int:
    return session.query(Verse).count()

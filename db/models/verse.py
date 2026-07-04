from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class Verse(Base):
    """
    A single Quran verse + translation, ingested from the Natiq Quran API.

    Postgres is the source of truth here; Redis only ever holds a cached
    copy of these rows for fast random access.
    """

    __tablename__ = "verses"
    __table_args__ = (
        UniqueConstraint(
            "mushaf", "translator_uuid", "surah_number", "verse_number",
            name="uq_verse_identity",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Id/uuid of this ayah as reported by the Natiq API, kept for traceability.
    external_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    mushaf: Mapped[str] = mapped_column(String(64))
    translator_uuid: Mapped[str] = mapped_column(String(64))

    surah_number: Mapped[int] = mapped_column(Integer)
    surah_name: Mapped[str] = mapped_column(String(255))
    verse_number: Mapped[int] = mapped_column(Integer)

    verse_text: Mapped[str] = mapped_column(Text)
    translation: Mapped[str] = mapped_column(Text)

    # "makki" / "madani" / "" (unknown)
    period: Mapped[str | None] = mapped_column(String(16), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

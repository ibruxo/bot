from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class SentMessage(Base):
    """Delivery history: every message the bot has sent out, on any
    platform."""

    __tablename__ = "sent_messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    platform: Mapped[str] = mapped_column(String(32), index=True)

    # The chat id on that platform this message was sent to.
    chat_id: Mapped[str] = mapped_column(String(128), index=True)

    # "user" / "group" / "channel" / "public" (public = group+channel broadcast)
    chat_type: Mapped[str] = mapped_column(String(16))

    verse_id: Mapped[int | None] = mapped_column(
        ForeignKey("verses.id", ondelete="SET NULL"), nullable=True
    )

    message_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

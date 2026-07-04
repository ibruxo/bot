from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class SentMessage(Base):
    """Delivery history: every message the bot has sent out."""

    __tablename__ = "sent_messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    # The Bale chat id this message was sent to (user, group, or channel).
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)

    # "user" / "group" / "channel"
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

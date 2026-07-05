from typing import Optional

from sqlalchemy.orm import Session

from db.models.sent_message import SentMessage


def log(
    session: Session,
    platform: str,
    chat_id: str,
    chat_type: str,
    verse_id: Optional[int],
    message_text: Optional[str],
    success: bool,
    error: Optional[str] = None,
) -> SentMessage:
    entry = SentMessage(
        platform=platform,
        chat_id=chat_id,
        chat_type=chat_type,
        verse_id=verse_id,
        message_text=message_text,
        success=success,
        error=error,
    )
    session.add(entry)
    return entry


def count(session: Session) -> int:
    return session.query(SentMessage).count()

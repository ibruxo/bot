from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.channel import Channel


def get_by_bale_id(session: Session, bale_chat_id: int) -> Optional[Channel]:
    stmt = select(Channel).where(Channel.bale_chat_id == bale_chat_id)
    return session.scalar(stmt)


def get_or_create(
    session: Session,
    bale_chat_id: int,
    title: Optional[str] = None,
    username: Optional[str] = None,
) -> Channel:
    channel = get_by_bale_id(session, bale_chat_id)

    if channel:
        if title is not None:
            channel.title = title
        if username is not None:
            channel.username = username
        channel.is_active = True
        return channel

    channel = Channel(bale_chat_id=bale_chat_id, title=title, username=username)
    session.add(channel)
    session.flush()
    return channel


def deactivate(session: Session, bale_chat_id: int) -> None:
    channel = get_by_bale_id(session, bale_chat_id)
    if channel:
        channel.is_active = False


def list_active_ids(session: Session) -> list[int]:
    stmt = select(Channel.bale_chat_id).where(Channel.is_active.is_(True))
    return list(session.scalars(stmt))


def count(session: Session) -> int:
    return session.query(Channel).count()

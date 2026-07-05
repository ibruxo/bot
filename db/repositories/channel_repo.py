from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.channel import Channel


def get_by_external_id(session: Session, platform: str, external_id: str) -> Optional[Channel]:
    stmt = select(Channel).where(Channel.platform == platform, Channel.external_id == external_id)
    return session.scalar(stmt)


def get_or_create(
    session: Session,
    platform: str,
    external_id: str,
    title: Optional[str] = None,
    username: Optional[str] = None,
) -> Channel:
    channel = get_by_external_id(session, platform, external_id)

    if channel:
        if title is not None:
            channel.title = title
        if username is not None:
            channel.username = username
        channel.is_active = True
        return channel

    channel = Channel(platform=platform, external_id=external_id, title=title, username=username)
    session.add(channel)
    session.flush()
    return channel


def deactivate(session: Session, platform: str, external_id: str) -> None:
    channel = get_by_external_id(session, platform, external_id)
    if channel:
        channel.is_active = False


def list_active(session: Session) -> list[tuple[str, str]]:
    stmt = select(Channel.platform, Channel.external_id).where(Channel.is_active.is_(True))
    return list(session.execute(stmt).all())


def count(session: Session) -> int:
    return session.query(Channel).count()

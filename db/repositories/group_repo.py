from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.group import Group


def get_by_bale_id(session: Session, bale_chat_id: int) -> Optional[Group]:
    stmt = select(Group).where(Group.bale_chat_id == bale_chat_id)
    return session.scalar(stmt)


def get_or_create(
    session: Session,
    bale_chat_id: int,
    title: Optional[str] = None,
) -> Group:
    group = get_by_bale_id(session, bale_chat_id)

    if group:
        if title is not None:
            group.title = title
        group.is_active = True
        return group

    group = Group(bale_chat_id=bale_chat_id, title=title)
    session.add(group)
    session.flush()
    return group


def deactivate(session: Session, bale_chat_id: int) -> None:
    group = get_by_bale_id(session, bale_chat_id)
    if group:
        group.is_active = False


def list_active_ids(session: Session) -> list[int]:
    stmt = select(Group.bale_chat_id).where(Group.is_active.is_(True))
    return list(session.scalars(stmt))


def count(session: Session) -> int:
    return session.query(Group).count()

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.group import Group


def get_by_external_id(session: Session, platform: str, external_id: str) -> Optional[Group]:
    stmt = select(Group).where(Group.platform == platform, Group.external_id == external_id)
    return session.scalar(stmt)


def get_or_create(
    session: Session,
    platform: str,
    external_id: str,
    title: Optional[str] = None,
) -> Group:
    group = get_by_external_id(session, platform, external_id)

    if group:
        if title is not None:
            group.title = title
        group.is_active = True
        return group

    group = Group(platform=platform, external_id=external_id, title=title)
    session.add(group)
    session.flush()
    return group


def deactivate(session: Session, platform: str, external_id: str) -> None:
    group = get_by_external_id(session, platform, external_id)
    if group:
        group.is_active = False


def list_active(session: Session) -> list[tuple[str, str]]:
    stmt = select(Group.platform, Group.external_id).where(Group.is_active.is_(True))
    return list(session.execute(stmt).all())


def count(session: Session) -> int:
    return session.query(Group).count()

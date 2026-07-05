from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.user import User


def get_by_external_id(session: Session, platform: str, external_id: str) -> Optional[User]:
    stmt = select(User).where(User.platform == platform, User.external_id == external_id)
    return session.scalar(stmt)


def get_or_create(
    session: Session,
    platform: str,
    external_id: str,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
) -> User:
    user = get_by_external_id(session, platform, external_id)

    if user:
        if username is not None:
            user.username = username
        if first_name is not None:
            user.first_name = first_name
        return user

    user = User(
        platform=platform,
        external_id=external_id,
        username=username,
        first_name=first_name,
    )
    session.add(user)
    session.flush()
    return user


def set_admin(session: Session, platform: str, external_id: str, is_admin: bool = True) -> Optional[User]:
    user = get_by_external_id(session, platform, external_id)
    if user:
        user.is_admin = is_admin
    return user


def is_admin(session: Session, platform: str, external_id: str) -> bool:
    user = get_by_external_id(session, platform, external_id)
    return bool(user and user.is_admin)


def list_active(session: Session) -> list[tuple[str, str]]:
    """Return [(platform, external_id), ...] for every active user."""
    stmt = select(User.platform, User.external_id).where(User.is_active.is_(True))
    return list(session.execute(stmt).all())


def count(session: Session) -> int:
    return session.query(User).count()

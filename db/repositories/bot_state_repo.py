from typing import Any, Optional

from sqlalchemy.orm import Session

from db.models.bot_state import BotState


def get(session: Session, key: str) -> Optional[Any]:
    state = session.get(BotState, key)
    return state.value if state else None


def set(session: Session, key: str, value: Any) -> None:
    state = session.get(BotState, key)
    if state:
        state.value = value
    else:
        session.add(BotState(key=key, value=value))

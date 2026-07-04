from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class BotState(Base):
    """Generic key/value store for small bits of persistent app state."""

    __tablename__ = "bot_state"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value: Mapped[dict] = mapped_column(JSON)

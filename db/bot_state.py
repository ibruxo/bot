from sqlalchemy import JSON

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from db.base import Base


class BotState(Base):

    __tablename__ = "bot_state"

    key: Mapped[str] = mapped_column(
        primary_key=True
    )

    value: Mapped[dict] = mapped_column(
        JSON
    )

import uuid

from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.models.base import Base
from app.database.models.mixins import (
    TimestampMixin,
    UUIDMixin,
)
from app.database.types import UUIDType


class ReadingProgress(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    """
    Stores the user's last reading position.
    """

    __tablename__ = "reading_progress"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        unique=True,
        index=True,
    )

    surah_uuid: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
    )

    ayah_uuid: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
    )

    user = relationship(
        "User",
        back_populates="reading_progress",
    )

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from users.user_profile import User

    from .trip import Trip

import uuid
from datetime import datetime as dt

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.database.database import Base
from app.users.user_profile.models import User


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str] = mapped_column(Text)
    created_at: Mapped[dt] = mapped_column(DateTime(timezone=True), default=dt.utcnow)

    # пользователь который оставляет отзыв
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    reviewer: Mapped["User"] = relationship(
        back_populates="reviews_given", foreign_keys=[reviewer_id]
    )

    # отзыв о попутчике
    reviewed_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    reviewed_user: Mapped["User"] = relationship(
        back_populates="reviews_received", foreign_keys=[reviewed_user_id]
    )

    # связь с поездкой
    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id")
    )
    trip: Mapped["Trip"] = relationship(back_populates="reviews")

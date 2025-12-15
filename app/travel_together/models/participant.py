from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from users.user_profile import User

    from .trip import Trip

import uuid
from datetime import datetime as dt
from enum import Enum

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.database.database import Base
from app.users.user_profile.models import User


class ParticipantStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    LEFT = "left"


class TripParticipant(Base):
    __tablename__ = "trip_participants"

    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id"), primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    status: Mapped[ParticipantStatus] = mapped_column(
        SQLEnum(ParticipantStatus), default=ParticipantStatus.PENDING
    )
    joined_at: Mapped[dt] = mapped_column(DateTime(timezone=True), default=dt.utcnow)

    trip: Mapped["Trip"] = relationship(back_populates="participants")
    user: Mapped["User"] = relationship(back_populates="participations")

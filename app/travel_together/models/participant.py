from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from users.user_profile import User
    from .trip import Trip

from enum import Enum
import uuid

from sqlalchemy import Enum as SQLEnum, ForeignKey, UniqueConstraint
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
    __table_args__ = (
        UniqueConstraint("trip_id", "user_id", name="uq_trip_participant"),
    )

    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id"), primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    status: Mapped[ParticipantStatus] = mapped_column(
        SQLEnum(ParticipantStatus), default=ParticipantStatus.PENDING
    )

    trip: Mapped["Trip"] = relationship(back_populates="participants")
    user: Mapped["User"] = relationship(back_populates="participations")

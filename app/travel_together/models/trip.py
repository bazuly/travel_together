from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .expense import Expense
    from .review import Review
    from .participant import TripParticipant
    from users.user_profile import User


from datetime import datetime as dt
import uuid
from uuid import uuid4

from sqlalchemy import String, Text, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.database.database import Base
from app.users.user_profile.models import User


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    destination: Mapped[str] = mapped_column(String(255))
    start_date: Mapped[dt] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[dt] = mapped_column(DateTime(timezone=True))
    budget_per_person: Mapped[float | None] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    is_public: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[dt] = mapped_column(DateTime(timezone=True), default=dt.utcnow)
    organizer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    organizer: Mapped["User"] = relationship(
        back_populates="trips_as_organizer", foreign_keys=[organizer_id]
    )
    participants: Mapped[list["TripParticipant"]] = relationship(
        back_populates="trip", cascade="all, delete-orphan"
    )
    expenses: Mapped[list["Expense"]] = relationship(
        back_populates="trip", cascade="all, delete-orphan"
    )
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="trip", cascade="all, delete-orphan"
    )

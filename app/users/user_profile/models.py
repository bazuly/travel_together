from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.travel_together.models import (
        Expense,
        ExpenseShare,
        Review,
        Trip,
        TripParticipant,
    )

import uuid
from uuid import uuid4

from sqlalchemy import String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.database.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(64), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    trips_as_organizer: Mapped[list["Trip"]] = relationship(
        back_populates="organizer", foreign_keys="Trip.organizer_id"
    )
    participations: Mapped[list["TripParticipant"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    expenses: Mapped[list["Expense"]] = relationship(back_populates="payer")
    expense_shares: Mapped[list["ExpenseShare"]
                           ] = relationship(back_populates="user")
    reviews_given: Mapped[list["Review"]] = relationship(
        foreign_keys="Review.reviewer_id", back_populates="reviewer"
    )
    reviews_received: Mapped[list["Review"]] = relationship(
        foreign_keys="Review.reviewed_user_id", back_populates="reviewed_user"
    )

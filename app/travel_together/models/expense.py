from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .expense_share import ExpenseShare
    from .trip import Trip
    from users.user_profile import User


from datetime import datetime as dt
from enum import Enum
import uuid

from sqlalchemy import Enum as SQLEnum, DateTime, String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.database.database import Base


class ExpenseCategory(str, Enum):
    ACCOMMODATION = "accommodation"
    FOOD = "food"
    TRANSPORT = "transport"
    ENTERTAIMENT = "entertaiment"
    OTHER = "other"


class Expense(Base):
    __tablename__ = "expenses"

    # TODO тоже исправить на uuid в предыдущих уроках
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(200))
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    category: Mapped[ExpenseCategory] = mapped_column(SQLEnum(ExpenseCategory))
    created_at: Mapped[dt] = mapped_column(DateTime(timezone=True), default=dt.utcnow)

    payer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    payer: Mapped["User"] = relationship(back_populates="expenses")

    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id")
    )
    trip: Mapped["Trip"] = relationship(back_populates="expenses")

    shared_with: Mapped[list["ExpenseShare"]] = relationship(
        back_populates="expense", cascade="all, delete-orphan"
    )

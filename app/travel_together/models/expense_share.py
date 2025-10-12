from __future__ import annotations
from typing import TYPE_CHECKING  # pep-563

if TYPE_CHECKING:
    from .expense import Expense
    from app.users.user_profile.models import User

import uuid

from sqlalchemy import ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.users.user_profile.models import User
from app.infra.database.database import Base


class ExpenseShare(Base):
    __tablename__ = "expense_shares"

    expense_id: Mapped[int] = mapped_column(
        ForeignKey("expenses.id"), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    share_amount: Mapped[float] = mapped_column(Float)

    expense: Mapped["Expense"] = relationship(back_populates="shared_with")
    user: Mapped["User"] = relationship(back_populates="expense_shares")

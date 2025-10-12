from datetime import datetime
from typing import List
import uuid

from pydantic import BaseModel

from app.travel_together.models import ExpenseCategory


class ExpenseShareCreate(BaseModel):
    user_id: uuid.UUID
    share_amount: float


class ExpenseCreate(BaseModel):
    description: str
    amount: float
    currency: str
    category: ExpenseCategory
    shared_with: List[ExpenseShareCreate]


class ExpenseResponse(ExpenseCreate):
    id: int
    payer_id: uuid.UUID
    trip_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.travel_together.models import ExpenseCategory


class ExpenseCreate(BaseModel):
    description: str
    amount: float
    currency: str = "USD"
    category: ExpenseCategory


class ExpenseResponse(ExpenseCreate):
    id: uuid.UUID
    created_at: datetime
    payer_id: uuid.UUID
    trip_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)

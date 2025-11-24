from datetime import datetime
import uuid

from pydantic import BaseModel

from app.travel_together.models import ExpenseCategory

# TODO переделать эти схемы в предыдущих урока


class ExpenseCreate(BaseModel):
    description: str
    amount: float
    currency: str = "USD"
    category: ExpenseCategory


# TODO переделать айдишники на интовые
class ExpenseResponse(ExpenseCreate):
    id: uuid.UUID
    created_at: datetime
    payer_id: uuid.UUID
    trip_id: uuid.UUID

    class Config:
        from_attributes = True

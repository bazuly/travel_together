import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TripCreate(BaseModel):
    title: str
    description: Optional[str] = None
    destination: str
    start_date: datetime
    end_date: datetime
    max_participants: int = Field(..., gt=1, le=10)
    budget_per_person: Optional[float] = None
    currency: str = "USD"
    is_public: bool = True


class TripResponse(TripCreate):
    id: uuid.UUID
    organizer_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

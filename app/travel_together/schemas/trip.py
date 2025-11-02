import uuid
from typing import Optional

from pydantic import BaseModel, Field
from datetime import datetime


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
    id: uuid.UUID = Field(..., json_schema_serialization_defaults={"type": "string"})
    # TODO: remove optional later
    organizer_id: Optional[uuid.UUID]
    created_at: datetime

    class Config:
        from_attributes = True

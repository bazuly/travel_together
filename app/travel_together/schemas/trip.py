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
    budget_per_person: Optional[float] = None
    currency: str = "USD"
    is_public: bool = True


class TripResponse(TripCreate):
    id: uuid.UUID = Field(..., json_schema_serialization_defaults={"type": "string"})
    organizer_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

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
    budget_per_person: Optional[float] = None
    currency: str = "USD"
    is_public: bool = True
    organizer_id: Optional[uuid.UUID] = None


class TripResponse(TripCreate):
    id: uuid.UUID = Field(..., json_schema_serialization_defaults={"type": "string"})  # type: ignore
    created_at: datetime

    class Config:
        from_attributes = True

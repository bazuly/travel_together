import uuid
from datetime import datetime

from pydantic import BaseModel


class ParticipantCreate(BaseModel):
    status: str
    joined_at: datetime


class ParticipantResponse(ParticipantCreate):
    trip_id: uuid.UUID
    user_id: uuid.UUID

    class Config:
        from_attributes = True

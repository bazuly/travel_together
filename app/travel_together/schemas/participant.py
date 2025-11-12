import uuid

from pydantic import BaseModel


class ParticipantCreate(BaseModel):
    status: str


class ParticipantResponse(ParticipantCreate):
    trip_id: uuid.UUID
    user_id: uuid.UUID

    class Config:
        from_attributes = True

import uuid

from pydantic import BaseModel, ConfigDict


class ParticipantCreate(BaseModel):
    status: str


class ParticipantResponse(ParticipantCreate):
    trip_id: uuid.UUID
    user_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)

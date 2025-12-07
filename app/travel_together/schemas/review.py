import uuid

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ReviewCreate(BaseModel):
    rating: int = Field(..., gt=1, le=10)
    comment: str


class ReviewResponse(ReviewCreate):
    id: int
    reviewer_id: uuid.UUID
    reviewed_user_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

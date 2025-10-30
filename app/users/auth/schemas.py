import uuid

from pydantic import BaseModel


class UserLoginSchema(BaseModel):
    user_id: uuid.UUID
    access_token: str

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    is_active: bool = True


class UserResponseSchema(BaseModel):
    id: UUID
    email: EmailStr
    password: str
    full_name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserUpdateSchema(UserCreateSchema): ...

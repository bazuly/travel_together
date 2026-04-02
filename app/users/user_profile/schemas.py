from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreateSchema(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str
    is_active: bool = True


class UserResponseSchema(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    password: str
    full_name: str
    is_active: bool

    class Config:
        from_attributes = True


class UserUpdateSchema(UserCreateSchema): ...

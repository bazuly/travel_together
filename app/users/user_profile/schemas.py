from pydantic import BaseModel


class UserCreateSchema(BaseModel):
    username: str | None = None
    password: str | None = None
    email: str | None = None
    yandex_access_token: str | None = None

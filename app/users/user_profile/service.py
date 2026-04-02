import uuid

from app.uow import UnitOfWork
from app.users.user_profile.security import hash_password

from .schemas import UserCreateSchema, UserResponseSchema


class UserService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_user(self, user_data: UserCreateSchema) -> UserResponseSchema:
        async with self.uow as uow:
            user_dict = user_data.model_dump()
            if "password" in user_dict:
                user_dict["password"] = hash_password(user_dict["password"])
            user = await uow.users.create_user(user_dict)
            return UserResponseSchema.model_validate(user)

    async def get_user_by_username(self, username: str) -> UserResponseSchema:
        async with self.uow as uow:
            user = await uow.users.get_user_by_username(username)
            return UserResponseSchema.model_validate(user)

    async def get_user_by_email(self, email: str) -> UserResponseSchema:
        async with self.uow as uow:
            user = await uow.users.get_user_by_email(email)
            return UserResponseSchema.model_validate(user)

    async def get_user_by_id(self, user_id: uuid.UUID) -> UserResponseSchema:
        async with self.uow as uow:
            user = await uow.users.get_user_by_id(user_id)
            return UserResponseSchema.model_validate(user)

    async def update_user(
        self, user_id: uuid.UUID, user_data: UserCreateSchema
    ) -> UserResponseSchema:
        async with self.uow as uow:
            user_dict = user_data.model_dump()
            user = await uow.users.update_user(user_id, user_dict)
            return UserResponseSchema.model_validate(user)

    async def delete_user(self, user_id: uuid.UUID) -> None:
        async with self.uow as uow:
            await uow.users.delete_user(user_id)

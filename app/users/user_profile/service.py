import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from .models import User
from .repository import UserRepository
from .schemas import UserCreateSchema, UserResponseSchema


class UserService:
    def __init__(self, db_session: AsyncSession):
        self.user_repository = UserRepository(db_session)

    async def create_user(self, user_data: UserCreateSchema) -> UserResponseSchema:
        user: User = await self.user_repository.create_user(user_data)
        return UserResponseSchema.model_validate(user)

    async def get_user_by_email(self, email: str) -> UserResponseSchema:
        user = await self.user_repository.get_user_by_email(email)
        return UserResponseSchema.model_validate(user)

    async def get_user_by_id(self, user_id: uuid.UUID) -> UserResponseSchema:
        user = await self.user_repository.get_user_by_id(user_id)
        return UserResponseSchema.model_validate(user)

    async def update_user(
        self, user_id: uuid.UUID, user_data: UserCreateSchema
    ) -> UserResponseSchema:
        user = await self.user_repository.update_user(user_id, user_data)
        return UserResponseSchema.model_validate(user)

    async def delete_user(self, user_id: uuid.UUID) -> None:
        await self.user_repository.delete_user(user_id)

import uuid

from sqlalchemy import delete, insert, select, update

from app.base_repository import BaseRepository
from app.exceptions import UserNotFoundError
from app.users.user_profile.models import User


class UserRepository(BaseRepository):
    async def create_user(self, user_data: dict) -> User | None:
        query = insert(User).values(**user_data).returning(User)
        result = await self._execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User:
        query = select(User).where(User.email == email)
        result = await self._execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            raise UserNotFoundError(email)
        return user

    async def get_user_by_username(self, username: str) -> User:
        query = select(User).where(User.username == username)
        result = await self._execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            raise UserNotFoundError(username)
        return user

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        query = select(User).where(User.id == user_id)
        result = await self._execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            raise UserNotFoundError(user_id)
        return user

    async def update_user(self, user_id: uuid.UUID, user_data: dict) -> User:
        query = (
            update(User).where(User.id == user_id).values(**user_data).returning(User)
        )
        result = await self._execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            raise UserNotFoundError(user_id)
        return user

    async def delete_user(self, user_id: uuid.UUID) -> bool:
        query = delete(User).where(User.id == user_id)
        result = await self._execute(query)
        if result.rowcount == 0:  # type: ignore
            raise UserNotFoundError(user_id)
        return result.rowcount > 0  # type: ignore

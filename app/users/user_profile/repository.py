from dataclasses import dataclass

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.user_profile.models import UserProfile
from app.users.user_profile.schema import UserCreateSchema


@dataclass
class UserRepository:
    db_session: AsyncSession

    async def create_user(self, user_data: UserCreateSchema) -> UserProfile:
        query = (
            insert(UserProfile)
            .values(**user_data.dict(exclude_none=True))
            .returning(UserProfile.id)
        )
        print(query)
        async with self.db_session as session:
            user_id: int = (await session.execute(query)).scalar()
            await session.commit()
            await session.flush()
            return await self.get_user(user_id)

    async def get_user(self, user_id: int) -> UserProfile | None:
        query = select(UserProfile).where(UserProfile.id == user_id)
        async with self.db_session as session:
            user = (await session.execute(query)).scalar_one_or_none()
            return user

    async def get_user_by_mail(self, email: str) -> UserProfile | None:
        query = select(UserProfile).where(UserProfile.email == email)
        async with self.db_session as session:
            user = (await session.execute(query)).scalar_one_or_none()
            return user

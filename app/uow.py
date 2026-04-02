from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class UnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def __aenter__(self):
        from app.travel_together.repository import TripRepository
        from app.users.user_profile.repository import UserRepository

        self.session = self.session_factory()
        self.trips = TripRepository(self.session)
        self.users = UserRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()

        await self.session.close()

    async def rollback(self) -> None:
        if self.session:
            await self.session.rollback()

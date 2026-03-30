from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.travel_together.repository import TripRepository


class UnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        self.trips = TripRepository(self.session)
        # new repos add here
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()

        await self.session.close()

    async def rollback(self) -> None:
        """Метод для явного отката, если логика требует этого вне исключений."""

        if self.session:
            await self.session.rollback()

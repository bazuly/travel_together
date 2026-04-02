from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def _execute(self, query):
        return await self.db_session.execute(query)

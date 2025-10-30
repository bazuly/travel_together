import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import RepositoryError


class BaseRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)

    async def _execute_read(self, query):
        try:
            return await self.db_session.execute(query)
        except SQLAlchemyError as e:
            self.logger.error("Database error: %s", str(e))
            raise RepositoryError(str(e))

    async def _execute_write(self, query):
        try:
            result = await self.db_session.execute(query)
            await self.db_session.commit()
            return result
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            self.logger.error("Database error: %s", str(e))
            raise RepositoryError(str(e))

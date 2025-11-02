from typing import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.exceptions import RepositoryError
from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.db_url, future=True, echo=True, pool_pre_ping=True
)

AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise RepositoryError(f"Database error: {str(e)}") from e
        finally:
            await session.close()

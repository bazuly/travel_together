import logging
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.travel_together.models import Trip
from app.exceptions import RepositoryError, TripNotFoundError
from .schemas import TripCreate


class BaseRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)

    async def _execute_and_commit(self, query, operation_name: str):
        try:
            result = await self.db_session.execute(query)
            await self.db_session.commit()
            self.logger.info("Operation complete %s: %s", operation_name)
            return result
        except RepositoryError as e:
            await self.db_session.rollback()
            self.logger.error("Error %s: %s", operation_name, str(e))
            raise HTTPException(status_code=500, detail=str(e))


class TripRepository(BaseRepository):
    async def create_trip(self, trip: TripCreate) -> Trip:
        query = insert(Trip).values(**trip.model_dump()).returning(Trip)
        result = await self._execute_and_commit(query, "trip creation")
        trip_data = result.scalars().one_or_none()
        return trip_data

    async def retrieve_trip(self, trip_id: UUID) -> Trip:
        query = select(Trip).where(Trip.id == trip_id)
        result = await self._execute_and_commit(query, "trip retrieval")
        trip_data = result.scalars().one_or_none()
        if trip_data is None:
            raise TripNotFoundError(str(trip_id))
        return trip_data

    async def update_trip(self, trip_id: UUID, trip: TripCreate) -> Trip:
        query = (
            update(Trip)
            .where(Trip.id == trip_id)
            .values(**trip.model_dump())
            .returning(Trip)
        )
        result = await self._execute_and_commit(query, "trip update")
        trip_data = result.scalars().one_or_none()
        if trip_data is None:
            raise TripNotFoundError(str(trip_id))
        return trip_data

    async def delete_trip(self, trip_id: UUID) -> dict:
        query = delete(Trip).where(Trip.id == trip_id)
        result = await self._execute_and_commit(query, "trip deletion")
        if result.rowcount == 0:
            raise TripNotFoundError(str(trip_id))
        return {"message": f"Trip {trip_id} deleted successfully"}

import uuid

from sqlalchemy import delete, insert, select, update

from app.base_repository import BaseRepository
from app.exceptions import TripNotFoundError
from app.travel_together.models import Trip


class TripRepository(BaseRepository):
    async def create_trip(self, trip_data: dict):
        query = insert(Trip).values(**trip_data).returning(Trip)
        result = await self._execute(query)
        return result.scalar_one_or_none()

    async def retrieve_trip(self, trip_id: uuid.UUID) -> Trip:
        query = select(Trip).where(Trip.id == trip_id)
        result = await self._execute(query)
        trip_data = result.scalars().one_or_none()
        if trip_data is None:
            raise TripNotFoundError(trip_id)
        return trip_data

    async def update_trip(self, trip_id: uuid.UUID, trip: dict) -> Trip:
        query = update(Trip).where(Trip.id == trip_id).values(**trip).returning(Trip)
        result = await self._execute(query)
        trip_data = result.scalars().one_or_none()
        if trip_data is None:
            raise TripNotFoundError(trip_id)
        return trip_data

    async def delete_trip(self, trip_id: uuid.UUID):
        query = delete(Trip).where(Trip.id == trip_id)
        result = await self._execute(query)
        if result.rowcount == 0:  # type: ignore
            raise TripNotFoundError(trip_id)
        return result.rowcount > 0  # type: ignore

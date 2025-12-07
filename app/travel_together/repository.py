import uuid

from sqlalchemy import insert, select, update, delete

from app.travel_together.models import Trip
from app.base_repository import BaseRepository
from app.exceptions import TripNotFoundError


class TripRepository(BaseRepository):
    async def create_trip(self, trip_data: dict) -> Trip:
        query = insert(Trip).values(**trip_data).returning(Trip)
        result = await self._execute_write(query)
        return result.scalar_one_or_none()

    async def retrieve_trip(self, trip_id: uuid.UUID) -> Trip:
        query = select(Trip).where(Trip.id == trip_id)
        result = await self._execute_read(query)
        trip_data = result.scalars().one_or_none()
        if trip_data is None:
            raise TripNotFoundError(str(trip_id))
        return trip_data

    async def retrieve_trip_for_update(self, trip_id: uuid.UUID) -> Trip:
        # with_for_update защита от race condition
        query = select(Trip).where(Trip.id == trip_id).with_for_update()
        result = await self._execute_read(query)
        trip_data = result.scalars().one_or_none()
        if trip_data is None:
            raise TripNotFoundError(str(trip_id))
        return trip_data

    async def update_trip(self, trip_id: uuid.UUID, trip: dict) -> Trip:
        query = update(Trip).where(
            Trip.id == trip_id).values(**trip).returning(Trip)
        result = await self._execute_write(query)
        trip_data = result.scalars().one_or_none()
        if trip_data is None:
            raise TripNotFoundError(str(trip_id))
        return trip_data

    async def delete_trip(self, trip_id: uuid.UUID) -> bool:
        query = delete(Trip).where(Trip.id == trip_id)
        result = await self._execute_write(query)
        if result.rowcount == 0:
            raise TripNotFoundError(str(trip_id))
        return result.rowcount > 0

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from .repository import TripRepository
from .schemas import TripCreate, TripResponse


class TripService:
    def __init__(self, db_session: AsyncSession):
        self.repo = TripRepository(db_session)

    async def create_trip(self, trip: TripCreate) -> TripResponse:
        trip = trip.model_dump()
        trip_data = await self.repo.create_trip(trip)
        return TripResponse.model_validate(trip_data)

    async def retrieve_trip(self, trip_id: uuid.UUID) -> TripResponse:
        trip = await self.repo.retrieve_trip(trip_id)
        return TripResponse.model_validate(trip)

    async def update_trip(self, trip_id: uuid.UUID, trip: TripCreate) -> TripResponse:
        trip = trip.model_dump()
        updated_trip = await self.repo.update_trip(trip_id, trip)
        return TripResponse.model_validate(updated_trip)

    async def delete_trip(self, trip_id: uuid.UUID) -> None:
        return await self.repo.delete_trip(trip_id)

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .repository import TripRepository
from .schemas import TripCreate, TripResponse


class TripService:
    def __init__(self, db_session: AsyncSession):
        self.repo = TripRepository(db_session)

    async def create_trip(self, trip: TripCreate) -> TripResponse:
        trip = await self.repo.create_trip(trip)
        return TripResponse.model_validate(trip)

    async def retrieve_trip(self, trip_id: UUID) -> TripResponse:
        trip = await self.repo.retrieve_trip(trip_id)
        return TripResponse.model_validate(trip)

    async def update_trip(self, trip_id: UUID, trip: TripCreate) -> TripResponse:
        trip = await self.repo.retrieve_trip(trip_id)
        return TripResponse.model_validate(trip)

    async def delete_trip(self, trip_id: UUID) -> None:
        return await self.repo.delete_trip(trip_id)

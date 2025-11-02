import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from .repository import TripRepository
from .schemas import TripCreate, TripResponse


class TripService:
    def __init__(self, db_session: AsyncSession):
        self.repo = TripRepository(db_session)

    async def create_trip(
        self, trip: TripCreate, current_user_id: uuid.UUID
    ) -> TripResponse:
        trip_data = trip.model_dump()
        trip_data["organizer_id"] = current_user_id

        trip = await self.repo.create_trip(trip_data)
        return TripResponse.model_validate(trip)

    async def retrieve_trip(self, trip_id: uuid.UUID) -> TripResponse:
        trip = await self.repo.retrieve_trip(trip_id)
        return TripResponse.model_validate(trip)

    async def update_trip(
        self, trip_id: uuid.UUID, trip: TripCreate, current_user_id: uuid.UUID
    ) -> TripResponse:
        existing_trip = await self.repo.retrieve_trip(trip_id)

        if existing_trip.organizer_id != current_user_id:
            raise PermissionError

        trip_data = trip.model_dump()
        # не меняем организатора + явно его сохраняем
        trip_data["organizer_id"] = existing_trip.organizer_id
        updated_trip = await self.repo.update_trip(trip_id, trip_data)

        return TripResponse.model_validate(updated_trip)

    async def delete_trip(self, trip_id: uuid.UUID, current_user_id: uuid.UUID) -> None:
        trip = await self.repo.retrieve_trip(trip_id)

        if trip.organizer_id != current_user_id:
            raise PermissionError

        return await self.repo.delete_trip(trip_id)

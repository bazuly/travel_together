import uuid

from app.uow import UnitOfWork

from .schemas import TripCreate, TripResponse


class TripService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_trip(self, trip: TripCreate) -> TripResponse:
        async with self.uow as uow:
            trip_dict = trip.model_dump()
            trip_data = await uow.trips.create_trip(trip_dict)
            return TripResponse.model_validate(trip_data)

    async def retrieve_trip(self, trip_id: uuid.UUID) -> TripResponse:
        async with self.uow as uow:
            trip_data = await uow.trips.retrieve_trip(trip_id)
            return TripResponse.model_validate(trip_data)

    async def update_trip(self, trip_id: uuid.UUID, trip: TripCreate) -> TripResponse:
        async with self.uow as uow:
            trip_data = trip.model_dump()
            updated_trip = await uow.trips.update_trip(trip_id, trip_data)
            return TripResponse.model_validate(updated_trip)

    async def delete_trip(self, trip_id: uuid.UUID):
        async with self.uow as uow:
            return uow.trips.delete_trip(trip_id)

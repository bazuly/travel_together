import uuid

from app.config import Settings
from app.travel_together.models.participant import ParticipanStatus
from .repository import TripRepository, ParticipantRepository
from .schemas import TripCreate, TripResponse, ParticipantResponse


class TripService:

    def __init__(
        self,
        trip_repo: TripRepository,
        participant_repo: ParticipantRepository,
    ):

        self.trip_repo = trip_repo
        self.participant_repo = participant_repo

    async def create_trip(
        self, trip: TripCreate, current_user_id: uuid.UUID
    ) -> TripResponse:
        trip_data = trip.model_dump()
        trip_data["organizer_id"] = current_user_id
        trip = await self.trip_repo.create_trip(trip_data)

        existing = await self.participant_repo.check_participant_exists(
            trip_id=trip.id, user_id=current_user_id
        )
        if not existing:
            await self.participant_repo.add_participant(
                trip_id=trip.id,
                current_user_id=current_user_id,
                status=ParticipanStatus.ACCEPTED,
            )
        return TripResponse.model_validate(trip)

    async def retrieve_trip(self, trip_id: uuid.UUID) -> TripResponse:
        trip = await self.trip_repo.retrieve_trip(trip_id)
        return TripResponse.model_validate(trip)

    async def update_trip(
        self, trip_id: uuid.UUID, trip: TripCreate, current_user_id: uuid.UUID
    ) -> TripResponse:
        existing_trip = await self.trip_repo.retrieve_trip(trip_id)

        if existing_trip.organizer_id != current_user_id:
            raise PermissionError

        trip_data = trip.model_dump()
        # не меняем организатора + явно его сохраняем
        trip_data["organizer_id"] = existing_trip.organizer_id
        updated_trip = await self.trip_repo.update_trip(trip_id, trip_data)

        return TripResponse.model_validate(updated_trip)

    async def delete_trip(self, trip_id: uuid.UUID, current_user_id: uuid.UUID) -> None:
        trip = await self.trip_repo.retrieve_trip(trip_id)

        # TODO: нужны наверное номральные ерроры
        if trip.organizer_id != current_user_id:
            raise PermissionError
        return await self.trip_repo.delete_trip(trip_id)


class ParticipantService:
    def __init__(
        self,
        trip_repo: TripRepository,
        participant_repo: ParticipantRepository,
    ):
        self.trip_repo = trip_repo
        self.participant_repo = participant_repo
        self.settings = Settings()

    async def add_participant(
        self, trip_id: uuid.UUID, user_id: uuid.UUID
    ) -> ParticipantResponse:
        # Используем retrieve_trip_for_update для блокировки строки
        # чтобы избежать состояние гонки
        trip = await self.trip_repo.retrieve_trip_for_update(trip_id)

        if trip.organizer_id == user_id:
            raise ValueError("Organizer is already a participant with ACCEPTED status.")

        current_amount_participants = await self.participant_repo.participants_count(
            trip_id
        )
        # TODO: Нормальный эксепшен нужен
        if current_amount_participants >= self.settings.MAX_PARTICIPANTS:
            raise ValueError("Reached max amount of participants")

        result = await self.participant_repo.add_participant(
            trip_id=trip_id, current_user_id=user_id, status=ParticipanStatus.PENDING
        )

        return ParticipantResponse.model_validate(result)

    async def remove_participant(self, trip_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        return await self.participant_repo.remove_participant(trip_id, user_id)

    async def retrieve_participants(
        self, trip_id: uuid.UUID
    ) -> list[ParticipantResponse]:
        items = await self.participant_repo.retrieve_participants(trip_id)
        return [ParticipantResponse.model_validate(item) for item in items]

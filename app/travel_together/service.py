import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.users.user_profile import UserRepository
from .repository import TripRepository, ParticipantRepository
from .schemas import TripCreate, TripResponse, ParticipantResponse


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

        # TODO: нужны наверное номральные ерроры
        if trip.organizer_id != current_user_id:
            raise PermissionError

        return await self.repo.delete_trip(trip_id)


class ParticipantService:
    def __init__(self, db_session: AsyncSession):
        self.user_repo = UserRepository(db_session)
        self.trip_repo = TripRepository(db_session)
        self.participant_repo = ParticipantRepository(
            db_session, self.user_repo, self.trip_repo
        )
        self.settings = Settings()

    async def add_participant(
        self, trip_id: uuid.UUID, user_id: uuid.UUID
    ) -> ParticipantResponse:
        # TODO остановился тут, на проверках
        # сонный с ватной головой, но на глазок вроде все нормально (нет)
        # TODO и добавить еще автомаитческое добавление организатора в качетсве участника
        # при создании поездки, но это конечно не в этом метода, очевидно
        trip = await self.trip_repo.retrieve_trip_for_update(trip_id)
        if trip.organizer_id == user_id:
            raise ValueError("oraganaizer is already participant")

        existing_participant = await self.participant_repo.check_participant_exists(
            user_id, trip_id
        )
        if existing_participant:
            raise ValueError(f"User {user_id} is already a participant")

        current_amount_participants = await self.participant_repo.participants_count(
            trip_id
        )
        if current_amount_participants >= self.settings.MAX_PARTICIPANTS:
            raise ValueError("reached max amount of participants")

        result = await self.participant_repo.add_participant(trip_id, user_id)
        return ParticipantResponse.model_validate(result)

    async def remove_participant(self, trip_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        return await self.participant_repo.remove_participant(trip_id, user_id)

    async def retrieve_participants(
        self, trip_id: uuid.UUID
    ) -> list[ParticipantResponse]:
        items = await self.participant_repo.retrieve_participants(trip_id)
        return [ParticipantResponse.model_validate(item) for item in items]

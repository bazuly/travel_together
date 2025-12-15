import uuid

from app.config import get_settings
from app.exceptions import (
    AlreadyTripParticipant,
    ReachedMaxParticipants,
    TripNotFoundError,
    TripOrganizerRequiredError,
)
from app.travel_together.models import ParticipantStatus
from app.travel_together.permissions import PermissionService

from .repository import ParticipantRepository, TripRepository
from .schemas import (
    ParticipantResponse,
    TripCreate,
    TripResponse,
)


class TripService:
    def __init__(
        self,
        trip_repo: TripRepository,
        participant_repo: ParticipantRepository,
        permission_service: PermissionService,
    ):
        self.trip_repo = trip_repo
        self.participant_repo = participant_repo
        self.permission_service = permission_service

    async def create_trip(self, trip: TripCreate, user_id: uuid.UUID) -> TripResponse:
        trip_data = trip.model_dump()
        trip_data["organizer_id"] = user_id
        trip = await self.trip_repo.create_trip(trip_data)

        return TripResponse.model_validate(trip)

    async def retrieve_trip(self, trip_id: uuid.UUID) -> TripResponse:
        trip = await self.trip_repo.retrieve_trip(trip_id)
        return TripResponse.model_validate(trip)

    async def update_trip(
        self, trip_id: uuid.UUID, trip: TripCreate, user_id: uuid.UUID
    ) -> TripResponse:
        existing_trip = await self.trip_repo.retrieve_trip(trip_id)

        if not await self.permission_service.check_is_user_trip_organizer(
            user_id, trip_id
        ):
            raise TripOrganizerRequiredError("Only the organizer can update this trip.")

        trip_data = trip.model_dump()
        trip_data["organizer_id"] = existing_trip.organizer_id
        updated_trip = await self.trip_repo.update_trip(trip_id, trip_data)

        return TripResponse.model_validate(updated_trip)

    async def delete_trip(self, trip_id: uuid.UUID, user_id: uuid.UUID) -> None:
        if not await self.permission_service.check_is_user_trip_organizer(
            user_id, trip_id
        ):
            raise TripOrganizerRequiredError("Only the organizer can delete this trip.")

        await self.trip_repo.delete_trip(trip_id)


class ParticipantService:
    def __init__(
        self,
        trip_repo: TripRepository,
        participant_repo: ParticipantRepository,
        permission_service: PermissionService,
    ):
        self.trip_repo = trip_repo
        self.participant_repo = participant_repo
        self.permission_service = permission_service
        self.settings = get_settings()

    async def add_participant(
        self, trip_id: uuid.UUID, user_id: uuid.UUID
    ) -> ParticipantResponse:
        # Используем retrieve_trip_for_update для блокировки строки
        # чтобы избежать состояние гонки
        trip = await self.trip_repo.retrieve_trip_for_update(trip_id)
        if await self.permission_service.check_is_user_trip_organizer(user_id, trip.id):
            raise AlreadyTripParticipant(
                "Organizer is already a participant with ACCEPTED status."
            )

        current_amount_participants = await self.participant_repo.participants_count(
            trip_id
        )

        if current_amount_participants >= self.settings.MAX_PARTICIPANTS:
            raise ReachedMaxParticipants("Reached max amount of participants")

        result = await self.participant_repo.add_participant(
            trip_id=trip_id, user_id=user_id, status=ParticipantStatus.PENDING
        )

        return ParticipantResponse.model_validate(result)

    async def retrieve_all_participants_from_trip(
        self, trip_id: uuid.UUID
    ) -> list[ParticipantResponse]:
        items = await self.participant_repo.retrieve_all_participants_from_trip(trip_id)
        return [ParticipantResponse.model_validate(item) for item in items]

    async def remove_participant(self, trip_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        trip = await self.trip_repo.retrieve_trip(trip_id)
        if not trip:
            raise TripNotFoundError(trip_id)
        is_organizer = await self.permission_service.check_is_user_trip_organizer(
            user_id, trip_id
        )
        is_participant_exists = (
            await self.permission_service.check_is_user_trip_participant(
                user_id, trip_id
            )
        )
        if not (is_organizer or is_participant_exists):
            raise TripOrganizerRequiredError(
                "Only the trip organizer or trip participant can remove trip member"
            )
        return await self.participant_repo.remove_participant(trip_id, user_id)

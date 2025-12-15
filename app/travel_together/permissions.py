import uuid

from app.exceptions import ParticipantNotFoundError
from app.travel_together.models import TripParticipant


class PermissionService:
    from app.travel_together.repository import (
        ParticipantRepository,
        TripRepository,
    )

    def __init__(
        self,
        trip_repo: TripRepository,
        participant_repo: ParticipantRepository,
    ):
        self.trip_repo = trip_repo
        self.participant_repo = participant_repo

    async def check_is_user_trip_organizer(
        self, user_id: uuid.UUID, trip_id: uuid.UUID
    ) -> bool:
        trip = await self.trip_repo.retrieve_trip(trip_id)
        return trip.organizer_id == user_id

    async def check_is_user_trip_participant(
        self, user_id: uuid.UUID, trip_id: uuid.UUID
    ) -> TripParticipant:
        participant = await self.participant_repo.retrieve_participant(trip_id, user_id)
        if not participant:
            raise ParticipantNotFoundError(participant_id=user_id, trip_id=trip_id)
        return participant

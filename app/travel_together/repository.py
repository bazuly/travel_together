import uuid

from sqlalchemy import insert, select, update, delete
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.travel_together.models import (
    Trip,
    TripParticipant,
    ParticipantStatus,
)
from app.users.user_profile import UserRepository
from app.base_repository import BaseRepository
from app.exceptions import (
    TripNotFoundError,
    ParticipantNotFoundError,
    ParticipantNotActiveError,
    AllParticipantFromTripError,
)


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
        if not result:
            raise TripNotFoundError(str(trip_id))
        return trip_data

    async def update_trip(self, trip_id: uuid.UUID, trip_data: dict) -> Trip:
        query = (
            update(Trip).where(Trip.id == trip_id).values(**trip_data).returning(Trip)
        )
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


class ParticipantRepository(BaseRepository):
    def __init__(
        self,
        db_session: AsyncSession,
        user_repo: UserRepository,
    ):
        super().__init__(db_session=db_session)
        self.user_repo = user_repo

    async def add_participant(
        self,
        trip_id: uuid.UUID,
        user_id: uuid.UUID,
        status=ParticipantStatus.PENDING,
    ) -> TripParticipant | None:

        user = await self.user_repo.get_user_by_id(user_id)
        if not user.is_active:
            raise ParticipantNotActiveError(str(user_id))

        stmt = (
            pg_insert(TripParticipant)
            .values(
                trip_id=trip_id,
                user_id=user.id,
                status=status,
            )
            .on_conflict_do_nothing(index_elements=["trip_id", "user_id"])
            .returning(TripParticipant)
        )
        result = await self._execute_write(stmt)
        return result.scalar_one_or_none()

    async def remove_participant(self, trip_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        query = delete(TripParticipant).where(
            TripParticipant.trip_id == trip_id, TripParticipant.user_id == user_id
        )
        result = await self._execute_write(query)
        if not result:
            raise ParticipantNotFoundError(participant_id=user_id, trip_id=trip_id)
        if result.rowcount == 0:
            raise ParticipantNotFoundError(str(user_id), str(trip_id))
        return result.rowcount > 0

    async def retrieve_participant(
        self, trip_id: uuid.UUID, user_id: uuid.UUID
    ) -> TripParticipant | None:
        query = select(TripParticipant).where(
            TripParticipant.user_id == user_id, TripParticipant.trip_id == trip_id
        )
        result = await self._execute_read(query)
        if not result:
            raise ParticipantNotFoundError(participant_id=user_id, trip_id=trip_id)
        return result.scalar_one_or_none()

    async def retrieve_all_participants_from_trip(
        self, trip_id: uuid.UUID
    ) -> list[TripParticipant]:
        query = select(TripParticipant).where(TripParticipant.trip_id == trip_id)
        result = await self._execute_read(query)
        if not result:
            raise AllParticipantFromTripError("Unable to retrieve all trip members")
        return result.scalars().all()

    async def participants_count(self, trip_id: uuid.UUID) -> int:
        query = (
            select(func.count())
            .select_from(TripParticipant)
            .where(TripParticipant.trip_id == trip_id)
        )
        result = await self._execute_read(query)
        return result.scalar_one()

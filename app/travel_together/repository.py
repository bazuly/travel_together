import uuid

from sqlalchemy import insert, select, update, delete
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.asyncio import AsyncSession


from app.travel_together.models import Trip, TripParticipan
from app.users.user_profile import UserRepository
from app.base_repository import BaseRepository
from app.exceptions import (
    TripNotFoundError,
    PartcipantNotFoundError,
    ParticipantNotActiveError,
    MaximunAmountOfParticipantsError,
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
        user_repo: UserRepository | None = None,
        trip_repo: TripRepository | None = None,
    ):
        # вызываем с помощью super, т.к. намн ужна одна сессия
        # создавать новую не нужно
        super().__init__(db_session)
        self.user_repo = user_repo or UserRepository(db_session)
        self.trip_repo = trip_repo or TripRepository(db_session)

    async def add_participant(
        self, trip_id: uuid.UUID, user_id: uuid.UUID
    ) -> TripParticipan:
        user = await self.user_repo.get_user_by_id(user_id)
        if not user.is_active:
            raise ParticipantNotActiveError(str(user_id))
        query = (
            insert(TripParticipan)
            .values(trip_id=trip_id, user_id=user_id)
            .returning(TripParticipan)
        )
        result = await self._execute_write(query)
        participant_data = result.scalar_one_or_none()
        return participant_data

    async def remove_participant(self, trip_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        query = delete(TripParticipan).where(
            TripParticipan.trip_id == trip_id, TripParticipan.user_id == user_id
        )
        result = await self._execute_write(query)
        if result.rowcount == 0:
            raise PartcipantNotFoundError(str(user_id), str(trip_id))
        return result.rowcount > 0

    async def retrieve_participants(self, trip_id: uuid.UUID) -> list[TripParticipan]:
        query = select(TripParticipan).where(TripParticipan.trip_id == trip_id)
        result = await self._execute_read(query)
        return result.scalars().all()

    async def participants_count(self, trip_id: uuid.UUID) -> int:
        query = (
            select(func.count())
            .select_from(TripParticipan)
            .where(TripParticipan.trip_id == trip_id)
        )
        result = await self._execute_read(query)
        return result.scalar_one()

    async def check_participant_exists(
        self, user_id: uuid.UUID, trip_id: uuid.UUID
    ) -> TripParticipan | None:
        query = select(TripParticipan).where(
            TripParticipan.trip_id == trip_id, TripParticipan.user_id == user_id
        )
        result = await self._execute_read(query)
        return result.scalar_one_or_none()

import uuid

from sqlalchemy import and_, delete, insert, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import func

from app.base_repository import BaseRepository
from app.exceptions import (
    AllParticipantFromTripError,
    ExpenseNotFoundError,
    ParticipantNotActiveError,
    ParticipantNotFoundError,
    TripNotFoundError,
)
from app.travel_together.models import (
    Expense,
    ParticipantStatus,
    Trip,
    TripParticipant,
)
from app.users.user_profile import UserRepository


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
        if trip_data is None:
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
        if result is None:
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
        if result is None:
            raise ParticipantNotFoundError(participant_id=user_id, trip_id=trip_id)
        return result.scalar_one_or_none()

    async def retrieve_all_participants_from_trip(
        self, trip_id: uuid.UUID
    ) -> list[TripParticipant]:
        query = select(TripParticipant).where(TripParticipant.trip_id == trip_id)
        result = await self._execute_read(query)
        if result is None:
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


class ExpenseRepository(BaseRepository):
    def __init__(
        self,
        db_session: AsyncSession,
        user_repo: UserRepository,
        trip_repo: TripRepository,
    ):
        super().__init__(db_session=db_session)
        self.user_repo = user_repo
        self.trip_repo = trip_repo

    async def create_trip_expense(
        self,
        trip_id: uuid.UUID,
        expense_data: dict,
        user_id: uuid.UUID,
    ) -> Expense:
        expense_id = uuid.uuid4()

        query = (
            insert(Expense)
            .values(
                id=expense_id,
                trip_id=trip_id,
                payer_id=user_id,
                description=expense_data["description"],
                amount=expense_data["amount"],
                currency=expense_data.get("currency", "USD"),
                category=expense_data["category"],
            )
            .returning(Expense)
        )
        result = await self._execute_write(query)
        return result.scalar_one()

    async def retrieve_trip_expense_by_expense_id(
        self, expense_id: uuid.UUID
    ) -> Expense | None:
        query = select(Expense).where(Expense.id == expense_id)
        result = await self._execute_read(query)
        if result is None:
            raise ExpenseNotFoundError(str(expense_id))
        return result.scalar_one_or_none()

    async def retrieve_trip_expense_by_trip_id(
        self, trip_id: uuid.UUID
    ) -> list[Expense] | None:
        query = select(Expense).where(Expense.trip_id == trip_id)
        result = await self._execute_read(query)
        if result is None:
            raise ExpenseNotFoundError(str(trip_id))
        return result.scalars().all()

    async def remove_trip_expense(self, expense_id: uuid.UUID) -> bool:
        query = delete(Expense).where(Expense.id == expense_id)
        result = await self._execute_write(query)
        if result is None:
            raise ExpenseNotFoundError(str(expense_id))
        return result.rowcount > 0

    async def update_trip_expense(
        self, expense_id: uuid.UUID, expense_data: dict
    ) -> Expense:
        query = (
            update(Expense)
            .where(Expense.id == expense_id)
            .values(**expense_data)
            .returning(Expense)
        )
        result = await self._execute_write(query)
        expense_data = result.scalars().one_or_none()
        if expense_data is None:
            raise ExpenseNotFoundError(str(expense_id))
        return expense_data

    async def get_complex_financial_report(
        self, trip_id: uuid.UUID, user_id: uuid.UUID
    ):
        participants_subquery = (
            select(func.count(TripParticipant.user_id))
            .where(TripParticipant.trip_id == trip_id)
            .scalar_subquery()
        )

        # траты конкретного пользователя
        user_spent_subquery = (
            select(func.coalesce(func.sum(Expense.amount), 0))
            .where(and_(Expense.trip_id == trip_id, Expense.payer_id == user_id))
            .scalar_subquery()  # Теперь вызываем у SELECT объекта
        )
        query = (
            select(
                Expense.category,
                func.sum(Expense.amount).label("category_amount"),
                func.sum(func.sum(Expense.amount)).over().label("total_trip_spent"),
                participants_subquery.label("participants_count"),
                user_spent_subquery.label("user_paid_total"),
            )
            .where(Expense.trip_id == trip_id)
            .group_by(Expense.category)
        )
        result = await self._execute_read(query)
        return result.all()

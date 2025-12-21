import uuid

from app.broker.producer import TripTaskProducer
from app.config import get_settings
from app.exceptions import (
    AlreadyTripParticipant,
    ExpenseNotFoundError,
    ExpensePayerRequiredError,
    ParticipantNotFoundError,
    ReachedMaxParticipants,
    TripNotFoundError,
    TripOrganizerRequiredError,
    UserNotFoundExceptionAuth,
)
from app.infra.cache.trip_cache import TripCache
from app.travel_together.models import ParticipantStatus
from app.travel_together.permissions import PermissionService

from .repository import ExpenseRepository, ParticipantRepository, TripRepository
from .schemas import (
    ExpenseCreate,
    ExpenseResponse,
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
        trip_cache: TripCache,
        trip_producer: TripTaskProducer,
    ):
        self.trip_repo = trip_repo
        self.trip_cache = trip_cache
        self.participant_repo = participant_repo
        self.permission_service = permission_service
        self.trip_producer = trip_producer

    async def create_trip(self, trip: TripCreate, user_id: uuid.UUID) -> TripResponse:
        trip_data = trip.model_dump()
        trip_data["organizer_id"] = user_id
        trip = await self.trip_repo.create_trip(trip_data)

        trip_schema = TripResponse.model_validate(trip)

        task_data = {
            "trip_id": str(trip_schema.id),
            "title": trip_schema.title,
            "destination": trip_schema.destination,
            "start_date": str(trip_schema.start_date),
        }
        await self.trip_producer.send_to_pdf_worker(task_data)

        return trip_schema

    async def retrieve_trip(self, trip_id: uuid.UUID) -> TripResponse:
        if cached_trip := await self.trip_cache.get_trip_from_cache(trip_id):
            return cached_trip
        else:
            trip = await self.trip_repo.retrieve_trip(trip_id)
            trip_schema = TripResponse.model_validate(trip)
            await self.trip_cache.set_trip_cache(trip_schema, trip_id)
            return trip_schema

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


class ExpenseService:
    def __init__(
        self,
        expense_repo: ExpenseRepository,
        permission_service: PermissionService,
    ):
        self.expense_repo = expense_repo
        self.permission_service = permission_service

    async def create_trip_expense(
        self,
        trip_id: uuid.UUID,
        expense: ExpenseCreate,
        user_id: uuid.UUID,
    ) -> ExpenseResponse:
        # Проверяем, что пользователь является участником органзитором или участником
        is_organizer = await self.permission_service.check_is_user_trip_organizer(
            user_id=user_id, trip_id=trip_id
        )
        if not is_organizer:
            try:
                await self.permission_service.check_is_user_trip_participant(
                    user_id=user_id, trip_id=trip_id
                )
            except ParticipantNotFoundError:
                raise UserNotFoundExceptionAuth(
                    "User is not a participant or organizer of this trip and cannot create expenses."
                )

        result = await self.expense_repo.create_trip_expense(
            trip_id=trip_id,
            expense_data=expense.model_dump(),
            user_id=user_id,
        )

        return ExpenseResponse.model_validate(result)

    async def retrieve_trip_expense_by_expense_id(
        self, expense_id: uuid.UUID
    ) -> ExpenseResponse:
        items = await self.expense_repo.retrieve_trip_expense_by_expense_id(expense_id)
        return ExpenseResponse.model_validate(items)

    async def retrieve_trip_expenses_by_trip_id(
        self, trip_id: uuid.UUID
    ) -> list[ExpenseResponse]:
        items = await self.expense_repo.retrieve_trip_expense_by_trip_id(trip_id)
        return [ExpenseResponse.model_validate(item) for item in items]

    async def update_trip_expense(
        self, expense_id: uuid.UUID, expense: ExpenseCreate, user_id: uuid.UUID
    ) -> ExpenseResponse:
        if not await self.permission_service.check_is_user_expense_creator(
            user_id, expense_id
        ):
            raise ExpensePayerRequiredError(expense_id)
        expense_data = expense.model_dump()
        updated_expense_data = await self.expense_repo.update_trip_expense(
            expense_id, expense_data
        )
        return ExpenseResponse.model_validate(updated_expense_data)

    async def remove_trip_expense(
        self, user_id: uuid.UUID, expense_id: uuid.UUID
    ) -> bool:
        expense = await self.expense_repo.retrieve_trip_expense_by_expense_id(
            expense_id
        )
        if expense is None:
            raise ExpenseNotFoundError(expense_id)

        is_organizer = await self.permission_service.check_is_user_trip_organizer(
            user_id, expense.trip_id
        )
        is_payer = expense.payer_id == user_id

        if not (is_organizer or is_payer):
            raise ExpensePayerRequiredError(expense_id)

        return await self.expense_repo.remove_trip_expense(expense_id)

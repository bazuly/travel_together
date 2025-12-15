from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.dependency import (
    get_expense_service,
    get_participant_service,
    get_trip_service,
    get_user_id,
)
from app.travel_together.schemas import (
    ExpenseCreate,
    ExpenseResponse,
    ParticipantResponse,
    TripCreate,
    TripResponse,
)
from app.travel_together.service import ExpenseService, ParticipantService, TripService

router = APIRouter(
    prefix="/trip",
    tags=["trip"],
)


@router.post(
    "/create_trip", response_model=TripResponse, status_code=status.HTTP_201_CREATED
)
async def create_trip(
    trip: TripCreate,
    trip_service: TripService = Depends(get_trip_service),
    user_id=Depends(get_user_id),
) -> TripResponse:
    return await trip_service.create_trip(trip, user_id)


@router.get(
    "/retrieve_trip/{trip_id}",
    response_model=TripResponse,
    status_code=status.HTTP_200_OK,
)
async def retrieve_trip(
    trip_id: UUID, trip_service: TripService = Depends(get_trip_service)
) -> TripResponse:
    return await trip_service.retrieve_trip(trip_id)


@router.put(
    "/update_trip/{trip_id}",
    response_model=TripResponse,
    status_code=status.HTTP_200_OK,
)
async def update_trip(
    trip_id: UUID,
    trip: TripCreate,
    trip_service: TripService = Depends(get_trip_service),
    user_id=Depends(get_user_id),
) -> TripResponse:
    return await trip_service.update_trip(trip_id, trip, user_id)


@router.delete("/delete_trip/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(
    trip_id: UUID,
    trip_service: TripService = Depends(get_trip_service),
    user_id=Depends(get_user_id),
) -> None:
    return await trip_service.delete_trip(trip_id, user_id)


@router.post("/participant_join/{trip_id}", status_code=status.HTTP_200_OK)
async def participant_join(
    trip_id: UUID,
    participant_service: ParticipantService = Depends(get_participant_service),
    user_id=Depends(get_user_id),
) -> ParticipantResponse:
    return await participant_service.add_participant(trip_id, user_id)


@router.get("/get_trip_participants/{trip_id}", status_code=status.HTTP_200_OK)
async def get_trip_participants(
    trip_id: UUID,
    participant_service: ParticipantService = Depends(get_participant_service),
) -> list[ParticipantResponse]:
    return await participant_service.retrieve_all_participants_from_trip(trip_id)


@router.delete("/participant_leave/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def participant_leave(
    trip_id: UUID,
    participant_service: ParticipantService = Depends(get_participant_service),
    user_id=Depends(get_user_id),
) -> None:
    return await participant_service.remove_participant(trip_id, user_id)


@router.post(
    "/create_trip_expense/{trip_id}",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_trip_expense(
    trip_id: UUID,
    expense: ExpenseCreate,
    expense_service: ExpenseService = Depends(get_expense_service),
    user_id: UUID = Depends(get_user_id),
) -> ExpenseResponse:
    return await expense_service.create_trip_expense(trip_id, expense, user_id)


@router.get(
    "/retrieve_trip_expense_by_trip_id/{trip_id}",
    response_model=list[ExpenseResponse],
    status_code=status.HTTP_200_OK,
)
async def retrieve_trip_expense_by_trip_id(
    trip_id: UUID, expense_service: ExpenseService = Depends(get_expense_service)
) -> list[ExpenseResponse]:
    return await expense_service.retrieve_trip_expenses_by_trip_id(trip_id)


@router.get(
    "/retrieve_expense_by_expense_id/{expense_id}",
    response_model=ExpenseResponse,
    status_code=status.HTTP_200_OK,
)
async def retrieve_trip_expense_by_expense_id(
    expense_id: UUID, expense_service: ExpenseService = Depends(get_expense_service)
) -> ExpenseResponse:
    return await expense_service.retrieve_trip_expense_by_expense_id(expense_id)


@router.put(
    "/update_trip_expense/{expense_id}",
    response_model=ExpenseResponse,
    status_code=status.HTTP_200_OK,
)
async def update_trip_expense(
    expense_id: UUID,
    expense: ExpenseCreate,
    user_id: UUID = Depends(get_user_id),
    expense_service: ExpenseService = Depends(get_expense_service),
) -> ExpenseResponse:
    return await expense_service.update_trip_expense(expense_id, expense, user_id)


@router.delete(
    "/remove_trip_expense/{expense_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_trip_expense(
    expense_id: UUID,
    user_id: UUID = Depends(get_user_id),
    expense_service: ExpenseService = Depends(get_expense_service),
) -> None:
    return await expense_service.remove_trip_expense(user_id, expense_id)

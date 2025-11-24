from uuid import UUID

from fastapi import Depends, APIRouter, status

from app.dependency import (
    get_trip_service,
    get_user_id,
    get_participant_service,
)
from app.travel_together.service import TripService, ParticipantService
from app.travel_together.schemas import (
    TripCreate,
    TripResponse,
    ParticipantResponse,
)


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

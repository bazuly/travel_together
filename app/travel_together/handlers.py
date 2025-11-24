from uuid import UUID

from fastapi import Depends, APIRouter, status

from app.dependency import get_trip_service, get_current_user_id
from app.travel_together.service import TripService
from app.travel_together.schemas import TripCreate, TripResponse


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
    current_user_id=Depends(get_current_user_id),
) -> TripResponse:
    return await trip_service.create_trip(trip, current_user_id)


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
    current_user_id=Depends(get_current_user_id),
) -> TripResponse:
    return await trip_service.update_trip(trip_id, trip, current_user_id)


@router.delete("/delete_trip/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(
    trip_id: UUID,
    trip_service: TripService = Depends(get_trip_service),
    current_user_id=Depends(get_current_user_id),
) -> None:
    return await trip_service.delete_trip(trip_id, current_user_id)

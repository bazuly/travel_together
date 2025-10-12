from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database.accessor import get_db_session
from app.travel_together.service import TripService


def get_trip_service(db_session: AsyncSession = Depends(get_db_session)) -> TripService:
    return TripService(db_session)

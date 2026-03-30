from fastapi import Depends

from app.infra.database.accessor import AsyncSessionFactory
from app.travel_together.service import TripService
from app.uow import UnitOfWork


def get_uow():
    return UnitOfWork(AsyncSessionFactory)


def get_trip_service(uow: UnitOfWork = Depends(get_uow)):
    return TripService(uow)

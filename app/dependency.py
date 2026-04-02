import uuid

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.infra.database.accessor import AsyncSessionFactory
from app.travel_together.service import TripService
from app.uow import UnitOfWork
from app.users.auth.service import AuthService
from app.users.user_profile.service import UserService

from .config import get_settings

settings = get_settings()
bearer_scheme = HTTPBearer(auto_error=True)


def get_uow():
    return UnitOfWork(AsyncSessionFactory)


def get_trip_service(uow: UnitOfWork = Depends(get_uow)):
    return TripService(uow)


def get_user_service(uow: UnitOfWork = Depends(get_uow)):
    return UserService(uow)


def get_auth_service(uow: UnitOfWork = Depends(get_uow)) -> AuthService:
    return AuthService(
        settings=settings,
        uow=uow,
    )


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> uuid.UUID:
    return await auth_service.decode_token(token=credentials.credentials)

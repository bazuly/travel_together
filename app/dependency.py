from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database.accessor import get_db_session
from app.travel_together.service import TripService
from app.users.auth.service import AuthService
from app.users.user_profile.service import UserService

from .config import get_settings

settings = get_settings()
bearer_scheme = HTTPBearer(auto_error=True)


def get_trip_service(db_session: AsyncSession = Depends(get_db_session)) -> TripService:
    return TripService(db_session)


def get_user_service(db_session: AsyncSession = Depends(get_db_session)) -> UserService:
    return UserService(db_session)


def get_auth_service(
    user_service: UserService = Depends(get_user_service),
) -> AuthService:
    return AuthService(
        settings=settings,
        user_service=user_service,
    )


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserService:
    return await auth_service.decode_token(token=credentials.credentials)

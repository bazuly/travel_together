import uuid

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.broker.producer import TripTaskProducer
from app.infra.cache.accessor import get_redis_connection
from app.infra.cache.trip_cache import TripCache
from app.infra.database.accessor import get_db_session
from app.travel_together.permissions import PermissionService
from app.travel_together.repository import (
    ExpenseRepository,
    ParticipantRepository,
    TripRepository,
    UserRepository,
)
from app.travel_together.service import ExpenseService, ParticipantService, TripService
from app.users.auth.service import AuthService
from app.users.user_profile.service import UserService

from .config import get_settings

settings = get_settings()
bearer_scheme = HTTPBearer(auto_error=True)


def get_user_repository(
    db_session: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    return UserRepository(db_session)


def get_trip_cache() -> TripCache:
    db_redis_session = get_redis_connection()
    return TripCache(db_redis_session)


def get_trip_producer() -> TripTaskProducer:
    return TripTaskProducer()


def get_trip_repository(
    db_session: AsyncSession = Depends(get_db_session),
) -> TripRepository:
    return TripRepository(db_session)


def get_participant_repository(
    db_session: AsyncSession = Depends(get_db_session),
    user_repo: UserRepository = Depends(get_user_repository),
) -> ParticipantRepository:
    return ParticipantRepository(
        db_session=db_session,
        user_repo=user_repo,
    )


def get_expense_repository(
    db_session: AsyncSession = Depends(get_db_session),
    user_repo: UserRepository = Depends(get_user_repository),
    trip_repo: TripRepository = Depends(get_trip_repository),
) -> ExpenseRepository:
    return ExpenseRepository(
        db_session=db_session, user_repo=user_repo, trip_repo=trip_repo
    )


def get_user_service(db_session: AsyncSession = Depends(get_db_session)) -> UserService:
    return UserService(db_session)


def get_auth_service(
    user_service: UserService = Depends(get_user_service),
) -> AuthService:
    return AuthService(
        settings=settings,
        user_service=user_service,
    )


async def get_user_id(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> uuid.UUID:
    return await auth_service.decode_token(token=credentials.credentials)


def get_permission_service(
    trip_repo: TripRepository = Depends(get_trip_repository),
    expense_repo: ExpenseRepository = Depends(get_expense_repository),
    participant_repo: ParticipantRepository = Depends(get_participant_repository),
) -> PermissionService:
    return PermissionService(
        trip_repo=trip_repo,
        expense_repo=expense_repo,
        participant_repo=participant_repo,
    )


def get_trip_service(
    trip_repo: TripRepository = Depends(get_trip_repository),
    trip_cache: TripCache = Depends(get_trip_cache),
    participant_repo: ParticipantRepository = Depends(get_participant_repository),
    permission_service: PermissionService = Depends(get_permission_service),
    trip_producer: TripTaskProducer = Depends(get_trip_producer),
) -> TripService:
    return TripService(
        trip_repo=trip_repo,
        participant_repo=participant_repo,
        permission_service=permission_service,
        trip_cache=trip_cache,
        trip_producer=trip_producer,
    )


def get_participant_service(
    trip_repo: TripRepository = Depends(get_trip_repository),
    participant_repo: ParticipantRepository = Depends(get_participant_repository),
    permission_service: PermissionService = Depends(get_permission_service),
) -> ParticipantService:
    return ParticipantService(
        trip_repo=trip_repo,
        participant_repo=participant_repo,
        permission_service=permission_service,
    )


def get_expense_service(
    expense_repo: ExpenseRepository = Depends(get_expense_repository),
    permission_service: PermissionService = Depends(get_permission_service),
) -> ExpenseService:
    return ExpenseService(
        expense_repo=expense_repo, permission_service=permission_service
    )

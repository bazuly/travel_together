import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Tuple

from fastapi import HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

from app.config import Settings
from app.exceptions import UserIncorrectPasswordException, UserNotFoundExceptionAuth
from app.uow import UnitOfWork
from app.users.auth import UserLoginSchema
from app.users.user_profile.security import verify_password

from ..user_profile.models import User

bearer_scheme = HTTPBearer(auto_error=True)


@dataclass
class AuthService:
    settings: Settings
    uow: UnitOfWork

    async def login(self, username: str, password: str) -> UserLoginSchema:
        async with self.uow as uow:
            user = await uow.users.get_user_by_username(username)
            self._validate_auth_user(user, password)

            # Generate both tokens
            access_token = self.create_token(
                user_id=user.id,
                expires_delta=timedelta(
                    minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
                ),
                token_type="regular_jwt_token",
            )
            refresh_token = self.create_token(
                user_id=user.id,
                expires_delta=timedelta(days=self.settings.REFRESH_TOKEN_EXPIRE_DAYS),
                token_type="refresh_token",
            )

            return UserLoginSchema(
                user_id=user.id, access_token=access_token, refresh_token=refresh_token
            )

    def create_token(
        self, user_id: uuid.UUID, expires_delta: timedelta, token_type: str = "access"
    ) -> str:
        expire = datetime.now(timezone.utc) + expires_delta

        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "type": token_type,
        }

        return jwt.encode(
            to_encode, self.settings.JWT_SECRET_KEY, algorithm=self.settings.ALGORITHM
        )

    async def refresh_tokens(self, refresh_token: str) -> Tuple[str, str]:
        """
        Validates a refresh token and returns a new pair of tokens.
        """
        try:
            payload = jwt.decode(
                refresh_token,
                self.settings.JWT_SECRET_KEY,
                algorithms=[self.settings.ALGORITHM],
            )

            if payload.get("type") != "refresh_token":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                )

            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                )

            new_access = self.create_token(
                user_id=uuid.UUID(user_id),
                expires_delta=timedelta(
                    minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
                ),
            )
            new_refresh = self.create_token(
                user_id=uuid.UUID(user_id),
                expires_delta=timedelta(days=self.settings.REFRESH_TOKEN_EXPIRE_DAYS),
                token_type="refresh_token",
            )

            return new_access, new_refresh

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired or invalid",
            )

    @staticmethod
    def _validate_auth_user(user: User, password: str):
        if not user:
            raise UserNotFoundExceptionAuth

        if not verify_password(password, user.password):
            raise UserIncorrectPasswordException(user.username)

    async def decode_token(self, token: str) -> uuid.UUID:
        payload = jwt.decode(
            token,
            self.settings.JWT_SECRET_KEY,
            algorithms=[self.settings.ALGORITHM],
        )

        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
            )
        return uuid.UUID(str(user_id))

    async def get_user_id(self, token: str):
        user_id = await self.decode_token(token)
        user = await self.user_service.get_user_by_id(user_id)  # type: ignore
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )
        return user

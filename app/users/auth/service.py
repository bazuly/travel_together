from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import uuid

from fastapi import HTTPException, status
from fastapi.security import HTTPBearer
from jose import jwt

from app.config import Settings
from app.exceptions import UserNotFoundExceptionAuth, UserIncorrectPasswordException
from app.users.auth import UserLoginSchema

from ..user_profile.service import UserService
from ..user_profile.models import User


bearer_scheme = HTTPBearer(auto_error=True)


@dataclass
class AuthService:
    settings: Settings
    user_service: UserService

    async def login(self, email: str, password: str) -> UserLoginSchema:
        user = await self.user_service.get_user_by_email(email)
        self._validate_auth_user(user, password)
        access_token = self.generate_access_token(user_id=user.id)

        return UserLoginSchema(user_id=user.id, access_token=access_token)

    @staticmethod
    def _validate_auth_user(user: User, password: str):
        if not user:
            raise UserNotFoundExceptionAuth
        if user.password != password:
            raise UserIncorrectPasswordException

    def generate_access_token(self, user_id: uuid.UUID) -> str:
        expires_data_unix = (datetime.now(timezone.utc) + timedelta(days=1)).timestamp()
        if isinstance(user_id, uuid.UUID):
            user_id = user_id.hex
        token = jwt.encode(
            {"user_id": user_id, "exp": expires_data_unix},
            self.settings.JWT_SECRET_KEY,
            algorithm=self.settings.ALGORITHM,
        )
        return token

    async def decode_token(self, token: str) -> uuid.UUID:
        payload = jwt.decode(
            token,
            self.settings.JWT_SECRET_KEY,
            algorithms=[self.settings.ALGORITHM],
        )

        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
            )
        print(uuid.UUID(str(user_id)))
        return uuid.UUID(str(user_id))

    async def get_current_user_id(self, token: str):
        user_id = self.decode_token(token)
        user = await self.user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )
        return user

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import uuid

from jose import jwt

from ..user_profile.service import UserService
from ..user_profile.models import User

from app.users.auth import UserLoginSchema
from app.exceptions import UserNotFoundExceptionAuth, UserIncorrectPasswordException
from app.config import Settings


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

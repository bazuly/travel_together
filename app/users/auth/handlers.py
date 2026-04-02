from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.dependency import get_auth_service
from app.users.auth import UserLoginSchema
from app.users.auth.service import AuthService
from app.users.user_profile import UserCreateSchema

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=UserLoginSchema, status_code=status.HTTP_200_OK)
async def login(
    body: UserCreateSchema,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    return await auth_service.login(username=body.username, password=body.password)

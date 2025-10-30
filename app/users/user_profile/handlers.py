import uuid

from fastapi import APIRouter, Depends, status

from app.dependency import get_user_service
from app.users.user_profile import UserService
from .schemas import UserCreateSchema, UserResponseSchema

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/create_user/",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_data: UserCreateSchema,
    service: UserService = Depends(get_user_service),
):
    return await service.create_user(user_data)


@router.get(
    "/retrieve_user_by_id/{user_id}",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_user(
    user_id: uuid.UUID,
    service: UserService = Depends(get_user_service),
):
    return await service.get_user_by_id(user_id)


@router.get(
    "/retrieve_user_by_email/{email}",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_user_by_email(
    email: str,
    service: UserService = Depends(get_user_service),
):
    return await service.get_user_by_email(email)


@router.put(
    "/update_user/{user_id}",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_id: uuid.UUID,
    user_data: UserCreateSchema,
    service: UserService = Depends(get_user_service),
):
    return await service.update_user(user_id, user_data)


@router.delete("/delete_user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    service: UserService = Depends(get_user_service),
):
    await service.delete_user(user_id)

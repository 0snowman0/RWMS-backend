from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from Configs.dependencies import get_unit_of_work
from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import (
    IUnitOfWork,
)
from Core.Domain.Models.user import User



router = APIRouter(
    tags=["Users"],
)


class CreateUserRequest(BaseModel):
    email: str
    full_name: str


class UpdateUserRequest(BaseModel):
    email: str
    full_name: str
    is_active: bool


UnitOfWorkDependency = Annotated[
    IUnitOfWork,
    Depends(get_unit_of_work),
]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    request: CreateUserRequest,
    uow: UnitOfWorkDependency,
):
    user = User(
        email=request.email,
        full_name=request.full_name,
        is_active=True,
    )

    await uow.users.add(user)

    await uow.save_changes()

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
    }


@router.get("")
async def get_users(
    uow: UnitOfWorkDependency,
):
    users = await uow.users.get_all()

    return [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }
        for user in users
    ]


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    uow: UnitOfWorkDependency,
):
    user = await uow.users.get(
        User.id == user_id
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    request: UpdateUserRequest,
    uow: UnitOfWorkDependency,
):
    user = await uow.users.get(
        User.id == user_id
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    user.email = request.email
    user.full_name = request.full_name
    user.is_active = request.is_active

    await uow.users.update(user)

    await uow.save_changes()

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
    }


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: int,
    uow: UnitOfWorkDependency,
):
    user = await uow.users.get(
        User.id == user_id
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    await uow.users.delete(user)

    await uow.save_changes()
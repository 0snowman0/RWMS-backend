from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from Configs.dependencies import get_mapper, get_unit_of_work
from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import IUnitOfWork
from Core.Application.Contracts.Mapper.mapper import IMapper
from Core.Application.DTOs.Users.Commands.user_test import UserCustomDto, UserDto
from Core.Domain.Models.user import User

router = APIRouter(
    prefix="/tests",
    tags=["Tests"],
)


MapperDependency = Annotated[
    IMapper,
    Depends(get_mapper),
]

UnitOfWorkDependency = Annotated[
    IUnitOfWork,
    Depends(get_unit_of_work),
]


@router.get("/{user_id}")
async def get_user_convert_DTO(
    user_id: int,
    uow: UnitOfWorkDependency,
    mapper: MapperDependency,
):
    target_user = await uow.users.get(
        User.id == user_id
    )

    if target_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    dto_data = mapper.map(
        target_user,
        UserDto,
    )

    return dto_data
    
@router.post("/simple-user-mapping")
async def simple_user_mapping(
    request: UserDto,
    mapper: MapperDependency,
    uow: UnitOfWorkDependency,
):
    user = mapper.map(
        request,
        User,
    )
    
    await uow.users.add(user)
    await uow.save_changes()
    
    return {
        "input": request.model_dump(),
        "output": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        },
    }


@router.post("/custom-user-mapping")
async def custom_user_mapping(
    request: UserCustomDto,
    mapper: MapperDependency,
):
    user = mapper.map(
        request,
        User,
    )

    return {
        "input": request.model_dump(),
        "output": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        },
    }
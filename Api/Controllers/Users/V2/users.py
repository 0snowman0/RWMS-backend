from fastapi import APIRouter, status

from Api.Configs.app_router import AppRouter
from Configs.dependencies import MediatorDependency
from Core.Application.DTOs.Users.Commands.user_test import UserCustomDto
from Core.Application.Features.Users.Requests.Commands.create_user import CreateUserCommand

router = AppRouter(
    tags=["Users"]
)



@router.post(
    "/mediator-test",
    status_code=status.HTTP_201_CREATED,
)
async def create_user_mediator_test(
    request: UserCustomDto,
    mediator: MediatorDependency,
):

    command = CreateUserCommand(
        data=request,
    )

    result = await mediator.send(
        command
    )

    return {
        "id": result.id,
        "email": result.email,
        "full_name": result.full_name,
        "is_active": result.is_active,
    }

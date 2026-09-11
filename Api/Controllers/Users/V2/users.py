from fastapi import APIRouter, status
from Api.Configs.app_router import AppRouter
from Api.Responses.api_response import to_api_response
from Configs.dependencies import MediatorDependency, MapperDependency
from Core.Application.DTOs.Users.Commands.user_test import UserCustomDto, UserDto
from Core.Application.Features.Users.Requests.Commands.create_user import CreateUserCommand
from Core.Domain.Models.user import User

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
    mapper: MapperDependency
):

    command = CreateUserCommand(
        data=request,
    )

    result = await mediator.send(
        command
    )
    
    dtoResult = mapper.map(
        result.data,
        UserDto
    )
    
    result.data = dtoResult
    
    return to_api_response(
        result=result
    )

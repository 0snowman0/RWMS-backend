from Api.Configs.app_router import AppRouter
from Api.Responses.api_response import to_api_response
from Core.Application.DTOs.Categories.category import (
    CreateCategoryDto,
    UpdateCategoryDto,
)

from Core.Application.Features.Categories.Requests.Commands.create_category import (
    CreateCategoryCommand,
)

from Configs.dependencies import (
    MediatorDependency,
)
from Core.Application.Features.Categories.Requests.Commands.delete_category import DeleteCategoryCommand
from Core.Application.Features.Categories.Requests.Commands.update_category import UpdateCategoryCommand
from Core.Application.Features.Categories.Requests.Queries.get_category_by_id import GetCategoryByIdQuery

router = AppRouter(
    tags=["category"]
)

@router.post(
    "/create",
)
async def create_category(
    request: CreateCategoryDto,
    mediator: MediatorDependency,
):

    command = CreateCategoryCommand(
        data=request,
    )

    result = await mediator.send(
        command
    )
    result.data = result.data.id
    return to_api_response(
        result=result
    )
    
    
@router.get(
    "/{category_id}",
)
async def get_category_by_id(
    category_id: int,
    mediator: MediatorDependency,
):

    query = GetCategoryByIdQuery(
        category_id=category_id,
    )

    result = await mediator.send(
        query
    )

    return to_api_response(
        result=result
    )


@router.put(
    "/{category_id}",
)
async def update_category(
    category_id: int,
    request: UpdateCategoryDto,
    mediator: MediatorDependency,
):

    command = UpdateCategoryCommand(
        category_id=category_id,
        data=request,
    )

    result = await mediator.send(
        command
    )

    return to_api_response(
        result=result
    )
    
    
    
@router.delete(
    "/{category_id}",
)
async def delete_category(
    category_id: int,
    mediator: MediatorDependency,
):

    command = DeleteCategoryCommand(
        category_id=category_id,
    )

    result = await mediator.send(
        command
    )

    return to_api_response(
        result=result
    )
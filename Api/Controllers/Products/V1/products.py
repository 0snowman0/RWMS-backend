from fastapi import Depends

from Api.Configs.app_router import (
    AppRouter,
)
from Api.Responses.api_response import (
    to_api_response,
)
from Configs.dependencies import (
    MediatorDependency,
)
from Core.Application.DTOs.Common.pagination_dto import (
    PagedRequestDto,
)
from Core.Application.DTOs.Products.product import (
    CreateProductDto,
    UpdateProductDto,
)
from Core.Application.Features.Products.Requests.Commands.create_product import (
    CreateProductCommand,
)
from Core.Application.Features.Products.Requests.Commands.update_product import (
    UpdateProductCommand,
)
from Core.Application.Features.Products.Requests.Commands.delete_product import (
    DeleteProductCommand,
)
from Core.Application.Features.Products.Requests.Queries.get_paged_products import (
    GetPagedProductsQuery,
)
from Core.Application.Features.Products.Requests.Queries.get_product_by_id import (
    GetProductByIdQuery,
)


router = AppRouter(
    tags=["product"]
)


@router.post(
    "/create",
)
async def create_product(
    request: CreateProductDto,
    mediator: MediatorDependency,
):

    command = CreateProductCommand(
        data=request,
    )

    result = await mediator.send(
        command
    )

    return {
        "is_success": result.is_success,
        "message": result.message,
        "errors": result.errors,
        "status": result.status,
    }


@router.get(
    "",
)
async def get_all_products(
    mediator: MediatorDependency,
    pagination: PagedRequestDto[None] = Depends(),
):
    query = GetPagedProductsQuery(
        pagination=pagination,
    )

    result = await mediator.send(
        query,
    )

    return to_api_response(
        result=result,
    )


@router.get(
    "/{product_id}",
)
async def get_product_by_id(
    product_id: int,
    mediator: MediatorDependency,
):

    query = GetProductByIdQuery(
        product_id=product_id,
    )

    result = await mediator.send(
        query
    )

    return result

@router.put(
    "/{product_id}",
)
async def update_product(
    product_id: int,
    request: UpdateProductDto,
    mediator: MediatorDependency,
):

    command = UpdateProductCommand(
        product_id=product_id,
        data=request,
    )

    result = await mediator.send(
        command
    )

    return {
        "is_success": result.is_success,
        "message": result.message,
        "errors": result.errors,
        "status": result.status,
    }


@router.delete(
    "/{product_id}",
)
async def delete_product(
    product_id: int,
    mediator: MediatorDependency,
):

    command = DeleteProductCommand(
        product_id=product_id,
    )

    result = await mediator.send(
        command
    )

    return result
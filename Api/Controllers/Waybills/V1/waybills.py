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
from Core.Application.DTOs.Waybills.waybill import (
    CreateWaybillDto,
    UpdateWaybillDto,
)
from Core.Application.Features.Waybills.Requests.Commands.create_waybill import (
    CreateWaybillCommand,
)
from Core.Application.Features.Waybills.Requests.Commands.delete_waybill import (
    DeleteWaybillCommand,
)
from Core.Application.Features.Waybills.Requests.Commands.update_waybill import (
    UpdateWaybillCommand,
)
from Core.Application.Features.Waybills.Requests.Queries.get_all_waybills import (
    GetAllWaybillsQuery,
)
from Core.Application.Features.Waybills.Requests.Queries.get_waybill_by_id import (
    GetWaybillByIdQuery,
)


router = AppRouter(
    tags=["Waybills"],
)


@router.post(
    "/create",
)
async def create_waybill(
    request: CreateWaybillDto,
    mediator: MediatorDependency,
):
    command = CreateWaybillCommand(
        data=request,
    )

    result = await mediator.send(
        command,
    )

    return to_api_response(
        result=result,
    )


@router.get(
    "",
)
async def get_all_waybills(
    mediator: MediatorDependency,
    pagination: PagedRequestDto[None] = Depends(),
    status: str | None = None,
    priority: str | None = None,
):
    query = GetAllWaybillsQuery(
        pagination=pagination,
        status=status,
        priority=priority,
    )

    result = await mediator.send(
        query,
    )

    return to_api_response(
        result=result,
    )


@router.get(
    "/{waybill_id}",
)
async def get_waybill_by_id(
    waybill_id: int,
    mediator: MediatorDependency,
):
    query = GetWaybillByIdQuery(
        waybill_id=waybill_id,
    )

    result = await mediator.send(
        query,
    )

    return to_api_response(
        result=result,
    )


@router.put(
    "/{waybill_id}",
)
async def update_waybill(
    waybill_id: int,
    request: UpdateWaybillDto,
    mediator: MediatorDependency,
):
    command = UpdateWaybillCommand(
        waybill_id=waybill_id,
        data=request,
    )

    result = await mediator.send(
        command,
    )

    return to_api_response(
        result=result,
    )


@router.delete(
    "/{waybill_id}",
)
async def delete_waybill(
    waybill_id: int,
    mediator: MediatorDependency,
):
    command = DeleteWaybillCommand(
        waybill_id=waybill_id,
    )

    result = await mediator.send(
        command,
    )

    return to_api_response(
        result=result,
    )

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
from Core.Application.DTOs.WaybillTemplates.waybill_template import (
    CreateWaybillTemplateDto,
    UpdateWaybillTemplateDto,
)
from Core.Application.Features.WaybillTemplates.Requests.Commands.create_waybill_template import (
    CreateWaybillTemplateCommand,
)
from Core.Application.Features.WaybillTemplates.Requests.Commands.delete_waybill_template import (
    DeleteWaybillTemplateCommand,
)
from Core.Application.Features.WaybillTemplates.Requests.Commands.update_waybill_template import (
    UpdateWaybillTemplateCommand,
)
from Core.Application.Features.WaybillTemplates.Requests.Queries.get_all_waybill_templates import (
    GetAllWaybillTemplatesQuery,
)
from Core.Application.Features.WaybillTemplates.Requests.Queries.get_waybill_template_by_id import (
    GetWaybillTemplateByIdQuery,
)


router = AppRouter(
    tags=["WaybillTemplates"],
)


@router.post(
    "/create",
)
async def create_waybill_template(
    request: CreateWaybillTemplateDto,
    mediator: MediatorDependency,
):
    command = CreateWaybillTemplateCommand(
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
async def get_all_waybill_templates(
    mediator: MediatorDependency,
    pagination: PagedRequestDto[None] = Depends(),
):
    query = GetAllWaybillTemplatesQuery(
        pagination=pagination,
    )

    result = await mediator.send(
        query,
    )

    return to_api_response(
        result=result,
    )


@router.get(
    "/{template_id}",
)
async def get_waybill_template_by_id(
    template_id: int,
    mediator: MediatorDependency,
):
    query = GetWaybillTemplateByIdQuery(
        template_id=template_id,
    )

    result = await mediator.send(
        query,
    )

    return to_api_response(
        result=result,
    )


@router.put(
    "/{template_id}",
)
async def update_waybill_template(
    template_id: int,
    request: UpdateWaybillTemplateDto,
    mediator: MediatorDependency,
):
    command = UpdateWaybillTemplateCommand(
        template_id=template_id,
        data=request,
    )

    result = await mediator.send(
        command,
    )

    return to_api_response(
        result=result,
    )


@router.delete(
    "/{template_id}",
)
async def delete_waybill_template(
    template_id: int,
    mediator: MediatorDependency,
):
    command = DeleteWaybillTemplateCommand(
        template_id=template_id,
    )

    result = await mediator.send(
        command,
    )

    return to_api_response(
        result=result,
    )

from Core.Application.Commons.base_response import (
    BaseResponse,
)
from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import (
    IUnitOfWork,
)
from Core.Application.Contracts.Mediators.mediator import (
    IRequestHandler,
)
from Core.Application.DTOs.Waybills.waybill import (
    WaybillDto,
)
from Core.Application.Features.Waybills.Helpers.waybill_dto_builder import (
    build_waybill_dto,
)
from Core.Application.Features.Waybills.Requests.Queries.get_waybill_by_id import (
    GetWaybillByIdQuery,
)
from Core.Application.Mediators.handler_decorators import (
    handler_for,
)
from Core.Domain.Models.WaybillTemplates.waybill_template import (
    WaybillTemplate,
)
from Core.Domain.Models.Waybills.waybill import (
    Waybill,
)


@handler_for(GetWaybillByIdQuery)
class GetWaybillByIdQueryHandler(
    IRequestHandler[
        GetWaybillByIdQuery,
        BaseResponse[WaybillDto],
    ]
):

    def __init__(
        self,
        uow: IUnitOfWork,
    ) -> None:

        self._uow = uow

    async def handle(
        self,
        request: GetWaybillByIdQuery,
    ) -> BaseResponse[WaybillDto]:

        waybill = await self._uow.waybills.get(
            Waybill.id == request.waybill_id
        )

        if waybill is None:
            return BaseResponse[WaybillDto].not_found(
                message="Waybill not found.",
            )

        if waybill.template is None:
            template = await self._uow.waybill_templates.get(
                WaybillTemplate.id == waybill.template_id
            )
            waybill.template = template

        waybill_dto = build_waybill_dto(
            waybill
        )

        return BaseResponse[WaybillDto].success(
            data=waybill_dto,
            message="Waybill retrieved successfully.",
        )

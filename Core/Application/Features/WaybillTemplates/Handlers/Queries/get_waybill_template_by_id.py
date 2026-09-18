from Core.Application.Commons.base_response import (
    BaseResponse,
)
from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import (
    IUnitOfWork,
)
from Core.Application.Contracts.Mapper.mapper import (
    IMapper,
)
from Core.Application.Contracts.Mediators.mediator import (
    IRequestHandler,
)
from Core.Application.DTOs.WaybillTemplates.waybill_template import (
    WaybillTemplateDto,
)
from Core.Application.Features.WaybillTemplates.Requests.Queries.get_waybill_template_by_id import (
    GetWaybillTemplateByIdQuery,
)
from Core.Application.Mediators.handler_decorators import (
    handler_for,
)
from Core.Domain.Models.WaybillTemplates.waybill_template import (
    WaybillTemplate,
)


@handler_for(GetWaybillTemplateByIdQuery)
class GetWaybillTemplateByIdQueryHandler(
    IRequestHandler[
        GetWaybillTemplateByIdQuery,
        BaseResponse[WaybillTemplateDto],
    ]
):

    def __init__(
        self,
        uow: IUnitOfWork,
        mapper: IMapper,
    ) -> None:

        self._uow = uow
        self._mapper = mapper

    async def handle(
        self,
        request: GetWaybillTemplateByIdQuery,
    ) -> BaseResponse[WaybillTemplateDto]:

        template = await self._uow.waybill_templates.get(
            WaybillTemplate.id == request.template_id
        )

        if template is None:
            return BaseResponse[WaybillTemplateDto].not_found(
                message="Waybill template not found.",
            )

        template_dto = self._mapper.map(
            template,
            WaybillTemplateDto,
        )

        return BaseResponse[WaybillTemplateDto].success(
            data=template_dto,
            message="Waybill template retrieved successfully.",
        )

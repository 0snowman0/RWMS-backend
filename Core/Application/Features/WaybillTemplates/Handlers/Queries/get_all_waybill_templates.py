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
    WaybillTemplateSummaryDto,
)
from Core.Application.Features.WaybillTemplates.Requests.Queries.get_all_waybill_templates import (
    GetAllWaybillTemplatesQuery,
)
from Core.Application.Mediators.handler_decorators import (
    handler_for,
)
from Core.Domain.Models.WaybillTemplates.waybill_template import (
    WaybillTemplate,
)


@handler_for(GetAllWaybillTemplatesQuery)
class GetAllWaybillTemplatesQueryHandler(
    IRequestHandler[
        GetAllWaybillTemplatesQuery,
        BaseResponse[list[WaybillTemplateSummaryDto]],
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
        request: GetAllWaybillTemplatesQuery,
    ) -> BaseResponse[list[WaybillTemplateSummaryDto]]:

        predicate = None
        if not request.include_inactive:
            predicate = (WaybillTemplate.is_active == True)

        templates = await self._uow.waybill_templates.get_all(
            predicate=predicate
        )

        template_dtos = self._mapper.map_list(
            templates,
            WaybillTemplateSummaryDto,
        )

        return BaseResponse[list[WaybillTemplateSummaryDto]].success(
            data=template_dtos,
            message="Waybill templates retrieved successfully.",
        )

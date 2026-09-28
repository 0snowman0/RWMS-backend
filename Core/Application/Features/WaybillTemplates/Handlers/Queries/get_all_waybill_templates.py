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
from Core.Application.DTOs.Common.pagination_dto import (
    PagedResultDto,
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


@handler_for(GetAllWaybillTemplatesQuery)
class GetAllWaybillTemplatesQueryHandler(
    IRequestHandler[
        GetAllWaybillTemplatesQuery,
        BaseResponse[PagedResultDto[WaybillTemplateSummaryDto]],
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
    ) -> BaseResponse[PagedResultDto[WaybillTemplateSummaryDto]]:

        paged_templates = await self._uow.waybill_templates.get_paged(
            pagination_params=request.pagination,
        )

        template_dtos = self._mapper.map_list(
            paged_templates.items,
            WaybillTemplateSummaryDto,
        )

        paged_result = PagedResultDto[WaybillTemplateSummaryDto].create(
            items=template_dtos,
            total_count=paged_templates.total_count,
            page_number=paged_templates.page_number,
            page_size=paged_templates.page_size,
        )

        return BaseResponse[PagedResultDto[WaybillTemplateSummaryDto]].success(
            data=paged_result,
            message="Waybill templates retrieved successfully.",
        )

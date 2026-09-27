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
from Core.Application.DTOs.Waybills.waybill import (
    WaybillSummaryDto,
)
from Core.Application.Features.Waybills.Requests.Queries.get_all_waybills import (
    GetAllWaybillsQuery,
)
from Core.Application.Mediators.handler_decorators import (
    handler_for,
)
from Core.Domain.Models.Waybills.waybill import (
    Waybill,
)


@handler_for(GetAllWaybillsQuery)
class GetAllWaybillsQueryHandler(
    IRequestHandler[
        GetAllWaybillsQuery,
        BaseResponse[PagedResultDto[WaybillSummaryDto]],
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
        request: GetAllWaybillsQuery,
    ) -> BaseResponse[PagedResultDto[WaybillSummaryDto]]:

        conditions = []
        if request.status:
            conditions.append(Waybill.status == request.status.lower())
        if request.priority:
            conditions.append(Waybill.priority == request.priority.lower())

        predicate = None
        if len(conditions) == 1:
            predicate = conditions[0]
        elif len(conditions) > 1:
            from sqlalchemy import and_
            predicate = and_(*conditions)

        paged_waybills = await self._uow.waybills.get_paged(
            predicate=predicate,
            pagination_params=request.pagination,
        )

        dtos = self._mapper.map_list(
            paged_waybills.items,
            WaybillSummaryDto,
        )

        paged_result = PagedResultDto[WaybillSummaryDto].create(
            items=dtos,
            total_count=paged_waybills.total_count,
            page_number=paged_waybills.page_number,
            page_size=paged_waybills.page_size,
        )

        return BaseResponse[PagedResultDto[WaybillSummaryDto]].success(
            data=paged_result,
            message="Waybills retrieved successfully.",
        )

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
        BaseResponse[list[WaybillSummaryDto]],
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
    ) -> BaseResponse[list[WaybillSummaryDto]]:

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

        waybills = await self._uow.waybills.get_all(
            predicate=predicate
        )

        dtos = self._mapper.map_list(
            waybills,
            WaybillSummaryDto,
        )

        return BaseResponse[list[WaybillSummaryDto]].success(
            data=dtos,
            message="Waybills retrieved successfully.",
        )

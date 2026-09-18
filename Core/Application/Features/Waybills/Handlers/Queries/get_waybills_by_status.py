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
from Core.Application.Features.Waybills.Requests.Queries.get_waybills_by_status import (
    GetWaybillsByStatusQuery,
)
from Core.Application.Mediators.handler_decorators import (
    handler_for,
)


@handler_for(GetWaybillsByStatusQuery)
class GetWaybillsByStatusQueryHandler(
    IRequestHandler[
        GetWaybillsByStatusQuery,
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
        request: GetWaybillsByStatusQuery,
    ) -> BaseResponse[list[WaybillSummaryDto]]:

        waybills = await self._uow.waybills.get_by_status(
            status=request.status.lower(),
        )

        dtos = self._mapper.map_list(
            waybills,
            WaybillSummaryDto,
        )

        return BaseResponse[list[WaybillSummaryDto]].success(
            data=dtos,
            message="Waybills retrieved successfully.",
        )

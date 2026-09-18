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
    WaybillDto,
)
from Core.Application.Features.Waybills.Requests.Queries.get_waybill_by_id import (
    GetWaybillByIdQuery,
)
from Core.Application.Mediators.handler_decorators import (
    handler_for,
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
        mapper: IMapper,
    ) -> None:

        self._uow = uow
        self._mapper = mapper

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

        waybill_dto = self._mapper.map(
            waybill,
            WaybillDto,
        )

        return BaseResponse[WaybillDto].success(
            data=waybill_dto,
            message="Waybill retrieved successfully.",
        )

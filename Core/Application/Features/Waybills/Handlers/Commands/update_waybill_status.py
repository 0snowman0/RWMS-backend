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
from Core.Application.Features.Waybills.Requests.Commands.update_waybill_status import (
    UpdateWaybillStatusCommand,
)
from Core.Application.Features.Waybills.Validators.status_transition_validator import (
    is_valid_transition,
)
from Core.Application.Mediators.handler_decorators import (
    handler_for,
)
from Core.Domain.Models.Waybills.waybill import (
    Waybill,
)


@handler_for(UpdateWaybillStatusCommand)
class UpdateWaybillStatusCommandHandler(
    IRequestHandler[
        UpdateWaybillStatusCommand,
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
        request: UpdateWaybillStatusCommand,
    ) -> BaseResponse[WaybillDto]:

        waybill = await self._uow.waybills.get(
            Waybill.id == request.waybill_id
        )

        if waybill is None:
            return BaseResponse[WaybillDto].not_found(
                message="Waybill not found.",
            )

        target_status = request.data.status.lower()

        if not is_valid_transition(waybill.status, target_status):
            return BaseResponse[WaybillDto].validation_error(
                message=(
                    f"Invalid status transition from '{waybill.status}' "
                    f"to '{target_status}'."
                ),
            )

        waybill.status = target_status

        waybill_dto = self._mapper.map(
            waybill,
            WaybillDto,
        )

        return BaseResponse[WaybillDto].success(
            data=waybill_dto,
            message="Waybill status updated successfully.",
        )

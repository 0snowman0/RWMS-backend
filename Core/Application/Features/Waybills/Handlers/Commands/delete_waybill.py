from Core.Application.Commons.base_response import (
    BaseResponse,
)
from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import (
    IUnitOfWork,
)
from Core.Application.Contracts.Mediators.mediator import (
    IRequestHandler,
)
from Core.Application.Features.Waybills.Requests.Commands.delete_waybill import (
    DeleteWaybillCommand,
)
from Core.Application.Mediators.handler_decorators import (
    handler_for,
)
from Core.Domain.Enums.Waybills.waybill_status import (
    WaybillStatus,
)
from Core.Domain.Models.Waybills.waybill import (
    Waybill,
)


@handler_for(DeleteWaybillCommand)
class DeleteWaybillCommandHandler(
    IRequestHandler[
        DeleteWaybillCommand,
        BaseResponse[bool],
    ]
):

    def __init__(
        self,
        uow: IUnitOfWork,
    ) -> None:

        self._uow = uow

    async def handle(
        self,
        request: DeleteWaybillCommand,
    ) -> BaseResponse[bool]:

        waybill = await self._uow.waybills.get(
            Waybill.id == request.waybill_id
        )

        if waybill is None:
            return BaseResponse[bool].not_found(
                message="Waybill not found.",
            )

        # Only REGISTERED and CANCELLED waybills can be deleted
        deletable_statuses = [
            WaybillStatus.REGISTERED.value,
            WaybillStatus.CANCELLED.value,
        ]

        if waybill.status not in deletable_statuses:
            return BaseResponse[bool].validation_error(
                message=(
                    f"Cannot delete waybill in '{waybill.status}' status. "
                    "Only 'registered' or 'cancelled' waybills can be deleted."
                ),
            )

        await self._uow.waybills.delete(
            waybill
        )

        return BaseResponse[bool].success(
            data=True,
            message="Waybill deleted successfully.",
        )

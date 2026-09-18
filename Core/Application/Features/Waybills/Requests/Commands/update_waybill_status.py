from dataclasses import dataclass

from Core.Application.Commons.base_response import (
    BaseResponse,
)
from Core.Application.Contracts.Mediators.mediator import (
    IRequest,
)
from Core.Application.DTOs.Waybills.waybill import (
    UpdateWaybillStatusDto,
    WaybillDto,
)
from Core.Application.Mediators.decorators import (
    request_type,
)
from Core.Domain.Enums.Mediators.mediator import (
    RequestType,
)


@request_type(
    RequestType.COMMAND
)
@dataclass(
    frozen=True,
    slots=True,
)
class UpdateWaybillStatusCommand(
    IRequest[
        BaseResponse[WaybillDto]
    ]
):

    waybill_id: int

    data: UpdateWaybillStatusDto

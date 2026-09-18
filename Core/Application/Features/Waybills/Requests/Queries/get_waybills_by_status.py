from dataclasses import dataclass

from Core.Application.Commons.base_response import (
    BaseResponse,
)
from Core.Application.Contracts.Mediators.mediator import (
    IRequest,
)
from Core.Application.DTOs.Waybills.waybill import (
    WaybillSummaryDto,
)
from Core.Application.Mediators.decorators import (
    request_type,
)
from Core.Domain.Enums.Mediators.mediator import (
    RequestType,
)


@request_type(
    RequestType.QUERY
)
@dataclass(
    frozen=True,
    slots=True,
)
class GetWaybillsByStatusQuery(
    IRequest[
        BaseResponse[list[WaybillSummaryDto]]
    ]
):

    status: str

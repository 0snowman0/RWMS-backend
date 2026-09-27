from dataclasses import dataclass, field

from Core.Application.Commons.base_response import (
    BaseResponse,
)
from Core.Application.Contracts.Mediators.mediator import (
    IRequest,
)
from Core.Application.DTOs.Common.pagination_dto import (
    PagedRequestDto,
    PagedResultDto,
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
class GetAllWaybillsQuery(
    IRequest[
        BaseResponse[PagedResultDto[WaybillSummaryDto]]
    ]
):

    pagination: PagedRequestDto[None] = field(
        default_factory=lambda: PagedRequestDto[None]()
    )
    status: str | None = None
    priority: str | None = None

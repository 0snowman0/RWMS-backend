from dataclasses import dataclass

from Core.Application.Commons.base_response import (
    BaseResponse,
)
from Core.Application.Contracts.Mediators.mediator import (
    IRequest,
)
from Core.Application.DTOs.AuditLogs.audit_log import (
    AuditLogDto,
)
from Core.Application.DTOs.Common.pagination_dto import (
    PagedRequestDto,
    PagedResultDto,
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
class GetPagedAuditLogsQuery(
    IRequest[
        BaseResponse[PagedResultDto[AuditLogDto]]
    ]
):

    pagination: PagedRequestDto[None]

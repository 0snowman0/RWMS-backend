from fastapi import Depends

from Api.Configs.app_router import AppRouter
from Api.Responses.api_response import to_api_response
from Configs.dependencies import (
    MediatorDependency,
)
from Core.Application.DTOs.Common.pagination_dto import (
    PagedRequestDto,
)
from Core.Application.Features.AuditLogs.Requests.Queries.get_paged_audit_logs import (
    GetPagedAuditLogsQuery,
)

router = AppRouter(
    tags=["AuditLogs"],
)


@router.get(
    "",
)
async def get_all_audit_logs(
    mediator: MediatorDependency,
    pagination: PagedRequestDto[None] = Depends(),
):
    query = GetPagedAuditLogsQuery(
        pagination=pagination,
    )

    result = await mediator.send(
        query,
    )

    return to_api_response(
        result=result,
    )

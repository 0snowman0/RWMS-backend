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
from Core.Application.DTOs.AuditLogs.audit_log import (
    AuditLogDto,
)
from Core.Application.DTOs.Common.pagination_dto import (
    PagedResultDto,
)
from Core.Application.Features.AuditLogs.Requests.Queries.get_paged_audit_logs import (
    GetPagedAuditLogsQuery,
)
from Core.Application.Mediators.handler_decorators import (
    handler_for,
)


@handler_for(GetPagedAuditLogsQuery)
class GetPagedAuditLogsQueryHandler(
    IRequestHandler[
        GetPagedAuditLogsQuery,
        BaseResponse[PagedResultDto[AuditLogDto]],
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
        request: GetPagedAuditLogsQuery,
    ) -> BaseResponse[PagedResultDto[AuditLogDto]]:

        paged_entities = await self._uow.audit_logs.get_paged(
            pagination_params=request.pagination,
        )

        audit_log_dtos = self._mapper.map_list(
            paged_entities.items,
            AuditLogDto,
        )

        paged_result = PagedResultDto[AuditLogDto].create(
            items=audit_log_dtos,
            total_count=paged_entities.total_count,
            page_number=paged_entities.page_number,
            page_size=paged_entities.page_size,
        )

        return BaseResponse[PagedResultDto[AuditLogDto]].success(
            data=paged_result,
            message="Audit logs retrieved successfully.",
        )

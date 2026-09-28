from sqlalchemy.ext.asyncio import AsyncSession

from Core.Application.Contracts.DataBases.Repositories.AuditLogs.audit_log_repository import (
    IAuditLogRepository,
)
from Core.Domain.Models.AuditLogs.audit_log import (
    AuditLog,
)
from Infrastructure.Persistence.Repositories.Generics.generic_repository import (
    GenericRepository,
)


class AuditLogRepository(
    GenericRepository[AuditLog],
    IAuditLogRepository,
):

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        super().__init__(
            session=session,
            entity_type=AuditLog,
        )

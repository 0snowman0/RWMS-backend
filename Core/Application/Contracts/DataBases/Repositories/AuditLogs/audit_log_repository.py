from typing import Protocol

from Core.Application.Contracts.DataBases.Repositories.Generics.repository import (
    IGenericRepository,
)
from Core.Domain.Models.AuditLogs.audit_log import (
    AuditLog,
)


class IAuditLogRepository(
    IGenericRepository[AuditLog],
    Protocol,
):
    pass

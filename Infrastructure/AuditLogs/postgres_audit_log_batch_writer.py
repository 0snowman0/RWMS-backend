from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession

from Core.Domain.Models.AuditLogs.audit_log import AuditLog
from Core.Domain.ViewModels.AuditLogs.audit_log_entry import AuditLogEntry


class PostgresAuditLogBatchWriter:
    """
    سرویس ذخیره‌سازی دسته‌ای رکوردهای ممیزی در دیتابیس PostgreSQL.
    """

    def __init__(
        self,
        session_factory: Callable[[], AsyncSession],
    ) -> None:
        self._session_factory = session_factory

    async def write(
        self,
        entries: list[AuditLogEntry],
    ) -> None:
        if not entries:
            return

        async with self._session_factory() as session:
            # جلوگیری از ممیزی عملیات خود ورکر
            session.info["skip_audit"] = True

            audit_models: list[AuditLog] = []
            for entry in entries:
                model = AuditLog(
                    table_name=entry.table_name,
                    action=entry.action,
                    old_values=entry.old_values,
                    new_values=entry.new_values,
                    primary_key=entry.primary_key,
                    user_id=entry.user_id,
                )
                if entry.created_at is not None:
                    model.created_at = entry.created_at

                audit_models.append(model)

            session.add_all(audit_models)
            await session.commit()

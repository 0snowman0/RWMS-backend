import asyncio

from Configs.AuditLogs.audit_log_settings import (
    AuditLogSettings,
)
from Core.Domain.ViewModels.AuditLogs.audit_log_entry import (
    AuditLogEntry,
)


class AsyncAuditLogQueue:
    """
    صف درون‌حافظه‌ای غیرمسدودکننده و ایمن برای جابجایی رکوردهای AuditLog.
    """

    def __init__(
        self,
        settings: AuditLogSettings,
    ) -> None:

        self._queue: asyncio.Queue[AuditLogEntry] = asyncio.Queue(
            maxsize=settings.max_queue_size
        )

    def enqueue(
        self,
        entry: AuditLogEntry,
    ) -> bool:
        """
        درج غیرمسدودکننده رکورد در صف.
        """
        try:
            self._queue.put_nowait(entry)
            return True
        except asyncio.QueueFull:
            return False

    async def dequeue(
        self,
    ) -> AuditLogEntry:
        """
        دریافت رکورد بعدی از صف به صورت ناهمگام.
        """
        return await self._queue.get()

    def task_done(
        self,
    ) -> None:
        self._queue.task_done()

    def size(
        self,
    ) -> int:
        return self._queue.qsize()

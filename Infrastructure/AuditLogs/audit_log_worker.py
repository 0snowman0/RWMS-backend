import asyncio
from typing import Sequence

from Configs.AuditLogs.audit_log_settings import (
    AuditLogSettings,
)
from Core.Domain.ViewModels.AuditLogs.audit_log_entry import (
    AuditLogEntry,
)
from Infrastructure.AuditLogs.async_audit_log_queue import (
    AsyncAuditLogQueue,
)
from Infrastructure.AuditLogs.postgres_audit_log_batch_writer import (
    PostgresAuditLogBatchWriter,
)


class AuditLogWorker:
    """
    سرویس پس‌زمینه (Background Service) برای خواندن ناهمگام لاگ‌ها از صف و درج دسته‌ای در دیتابیس.
    پشتیبانی از فلاش چندشرطی (تعداد لاگ + بازه زمانی) و توقف تمیز (Graceful Shutdown).
    """

    def __init__(
        self,
        queue: AsyncAuditLogQueue,
        batch_writer: PostgresAuditLogBatchWriter,
        settings: AuditLogSettings,
    ) -> None:
        self._queue = queue
        self._batch_writer = batch_writer
        self._settings = settings

        self._stop_event = asyncio.Event()
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        """
        راه‌اندازی سرویس پس‌زمینه.
        """
        if self._task is not None and not self._task.done():
            return

        self._stop_event.clear()
        self._task = asyncio.create_task(
            self._run(),
            name="audit-log-worker",
        )

    async def stop(self) -> None:
        """
        توقف تمیز سرویس پس‌زمینه همراه با تخلیه لاگ‌های باقی‌مانده.
        """
        if self._task is None:
            return

        self._stop_event.set()
        await self._task
        self._task = None

    async def _run(self) -> None:
        batch: list[AuditLogEntry] = []

        while not self._stop_event.is_set():
            # تعیین تایم‌اوت بر اساس تنظیمات زمان‌بندی
            timeout = None
            if batch:
                if self._settings.batching.enable_periodic_flush:
                    timeout = self._settings.batching.flush_interval_in_seconds
                else:
                    timeout = None

            state, entry = await self._wait_for_entry(timeout=timeout)

            # ۱. لاگ جدید از صف دریافت شد
            if state == "entry":
                if entry is None:
                    continue

                batch.append(entry)

                if len(batch) >= self._settings.batching.batch_size:
                    await self._flush(batch)
                    batch.clear()

                continue

            # ۲. بازه زمانی به پایان رسید و لاگ‌ها باید تخلیه شوند
            if state == "timeout":
                if batch:
                    await self._flush(batch)
                    batch.clear()
                continue

            # ۳. درخواست توقف سرویس دریافت شد
            if state == "stop":
                break

        # تخلیه لاگ‌های باقی‌مانده در صف در زمان شات‌دان
        await self._flush_remaining(batch)

    async def _wait_for_entry(
        self,
        timeout: float | None,
    ) -> tuple[str, AuditLogEntry | None]:
        dequeue_task = asyncio.create_task(self._queue.dequeue())
        stop_task = asyncio.create_task(self._stop_event.wait())

        done, pending = await asyncio.wait(
            {dequeue_task, stop_task},
            timeout=timeout,
            return_when=asyncio.FIRST_COMPLETED,
        )

        # شرایط تایم‌اوت
        if not done:
            await self._cancel_tasks(dequeue_task, stop_task)
            return ("timeout", None)

        if dequeue_task in done:
            entry = dequeue_task.result()
            if not stop_task.done():
                stop_task.cancel()
                await asyncio.gather(stop_task, return_exceptions=True)
            return ("entry", entry)

        if not dequeue_task.done():
            dequeue_task.cancel()
            await asyncio.gather(dequeue_task, return_exceptions=True)

        return ("stop", None)

    async def _flush(self, batch: Sequence[AuditLogEntry]) -> None:
        if not batch:
            return

        entries = list(batch)
        try:
            await self._batch_writer.write(entries)
        except Exception:
            # مانع از متوقف شدن چرخه پس‌زمینه به دلیل خطای موقت دیتابیس
            pass
        finally:
            for _ in entries:
                self._queue.task_done()

    async def _flush_remaining(self, batch: list[AuditLogEntry]) -> None:
        """
        تخلیه کامل تمام لاگ‌های موجود در صف در زمان بستن برنامه.
        """
        while self._queue.size() > 0:
            try:
                entry = await self._queue.dequeue()
                batch.append(entry)

                if len(batch) >= self._settings.batching.batch_size:
                    await self._flush(batch)
                    batch.clear()
            except Exception:
                break

        if batch:
            await self._flush(batch)
            batch.clear()

    async def _cancel_tasks(self, *tasks: asyncio.Task) -> None:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

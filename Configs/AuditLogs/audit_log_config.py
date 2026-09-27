from fastapi import FastAPI

from Configs.AuditLogs.audit_log_settings import (
    AuditLogSettings,
)
from Infrastructure.AuditLogs.async_audit_log_queue import (
    AsyncAuditLogQueue,
)
from Infrastructure.AuditLogs.audit_log_interceptor import (
    AuditLogInterceptor,
)
from Infrastructure.AuditLogs.audit_log_worker import (
    AuditLogWorker,
)
from Infrastructure.AuditLogs.postgres_audit_log_batch_writer import (
    PostgresAuditLogBatchWriter,
)
from Infrastructure.Persistence.Configs.PGdatabase import (
    AsyncSessionLocal,
)


def configure_audit_logging(
    app: FastAPI,
) -> None:
    """
    پیکربندی و راه‌اندازی زیرسیستم ممیزی دیتابیس (Audit Logging).
    """

    # ۱. بارگذاری تنظیمات از appsettings.json
    settings = AuditLogSettings.load_from_file_or_default("appsettings.json")

    # ۲. ایجاد صف درون‌حافظه‌ای
    queue = AsyncAuditLogQueue(settings=settings)

    # ۳. ایجاد سرویس ذخیره‌ساز دسته‌ای
    batch_writer = PostgresAuditLogBatchWriter(
        session_factory=AsyncSessionLocal,
    )

    # ۴. ایجاد کارگر پس‌زمینه
    worker = AuditLogWorker(
        queue=queue,
        batch_writer=batch_writer,
        settings=settings,
    )

    # ۵. ایجاد و اتصال اینترسپتور به سشن‌های SQLAlchemy
    interceptor = AuditLogInterceptor(
        queue=queue,
        settings=settings,
    )
    interceptor.attach()

    # ۶. ثبت در وضعیت اپلیکیشن (App State)
    app.state.audit_log_settings = settings
    app.state.audit_log_queue = queue
    app.state.audit_log_batch_writer = batch_writer
    app.state.audit_log_worker = worker
    app.state.audit_log_interceptor = interceptor

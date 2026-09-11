from fastapi import FastAPI

from Configs.Loggings.logging_settings import (
    LoggingSettings,
)

from Infrastructure.Loggings.application_logger import (
    ApplicationLogger,
)

from Infrastructure.Loggings.async_log_queue import (
    AsyncLogQueue,
)

from Infrastructure.Loggings.file_log_fallback_writer import (
    FileLogFallbackWriter,
)

from Infrastructure.Loggings.log_worker import (
    LogWorker,
)

from Infrastructure.Loggings.postgres_log_batch_writer import (
    PostgresLogBatchWriter,
)

from Infrastructure.Persistence.Configs.PGdatabase import (
    AsyncSessionLocal,
)


def configure_logging(
    app: FastAPI,
) -> None:

    # =========================================================
    # Settings
    # =========================================================

    settings = LoggingSettings()

    # =========================================================
    # Queue
    # =========================================================

    log_queue = AsyncLogQueue(
        settings=settings,
    )

    # =========================================================
    # Fallback File
    # =========================================================

    fallback_writer = FileLogFallbackWriter(
        settings=settings,
    )

    # =========================================================
    # PostgreSQL Batch Writer
    # =========================================================

    batch_writer = PostgresLogBatchWriter(
        session_factory=AsyncSessionLocal,
    )

    # =========================================================
    # Application Logger
    # =========================================================

    application_logger = ApplicationLogger(
        settings=settings,
        log_queue=log_queue,
        fallback_writer=fallback_writer,
    )

    # =========================================================
    # Background Worker
    # =========================================================

    log_worker = LogWorker(
        log_queue=log_queue,
        batch_writer=batch_writer,
        fallback_writer=fallback_writer,
        settings=settings,
    )

    # =========================================================
    # App State
    # =========================================================

    app.state.logging_settings = settings

    app.state.log_queue = (
        log_queue
    )

    app.state.log_fallback_writer = (
        fallback_writer
    )

    app.state.log_batch_writer = (
        batch_writer
    )

    app.state.application_logger = (
        application_logger
    )

    app.state.log_worker = (
        log_worker
    )
    

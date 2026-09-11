import logging
import traceback
from typing import Any

from Configs.Loggings.logging_settings import (
    LoggingSettings,
)

from Core.Application.Contracts.Loggings.log_fallback_writer import (
    ILogFallbackWriter,
)

from Core.Application.Contracts.Loggings.log_queue import (
    ILogQueue,
)

from Core.Application.Contracts.Loggings.logger import (
    ILogger,
)

from Core.Application.Loggings.logging_context import (
    LoggingContextAccessor,
)

from Core.Domain.Enums.Loggings.log_level import (
    LogLevel,
)

from Core.Domain.ViewModels.Loggings.log_entry import (
    LogEntry,
)


class ApplicationLogger(
    ILogger,
):

    def __init__(
        self,
        settings: LoggingSettings,
        log_queue: ILogQueue,
        fallback_writer: ILogFallbackWriter,
        logger_name: str = "Application",
    ):
        self._settings = settings
        self._log_queue = log_queue
        self._fallback_writer = fallback_writer
        self._logger_name = logger_name

        self._console_logger = logging.getLogger(
            logger_name
        )

    # =========================================================
    # Main Log
    # =========================================================

    def log(
        self,
        level: LogLevel,
        message: str,
        properties: dict[str, Any] | None = None,
        exception: Exception | None = None,
    ) -> None:

        if not self._settings.enabled:
            return

        if level < self._settings.minimum_level:
            return

        entry = self._create_entry(
            level=level,
            message=message,
            properties=properties,
            exception=exception,
        )

        if self._settings.console_enabled:
            self._write_console(
                entry,
                exception,
            )

        if not self._settings.database_enabled:
            return

        queued = self._log_queue.enqueue(
            entry
        )

        if (
            not queued
            and self._settings.fallback_to_file
        ):
            try:

                self._fallback_writer.write(
                    [entry]
                )

            except Exception:
                pass

    # =========================================================
    # Levels
    # =========================================================

    def debug(
        self,
        message: str,
        properties: dict[str, Any] | None = None,
    ) -> None:

        self.log(
            LogLevel.DEBUG,
            message,
            properties,
        )

    def info(
        self,
        message: str,
        properties: dict[str, Any] | None = None,
    ) -> None:

        self.log(
            LogLevel.INFO,
            message,
            properties,
        )

    def warning(
        self,
        message: str,
        properties: dict[str, Any] | None = None,
    ) -> None:

        self.log(
            LogLevel.WARNING,
            message,
            properties,
        )

    def error(
        self,
        message: str,
        properties: dict[str, Any] | None = None,
        exception: Exception | None = None,
    ) -> None:

        self.log(
            LogLevel.ERROR,
            message,
            properties,
            exception,
        )

    def critical(
        self,
        message: str,
        properties: dict[str, Any] | None = None,
        exception: Exception | None = None,
    ) -> None:

        self.log(
            LogLevel.CRITICAL,
            message,
            properties,
            exception,
        )

    def exception(
        self,
        message: str,
        exception: Exception,
        properties: dict[str, Any] | None = None,
    ) -> None:

        self.log(
            LogLevel.ERROR,
            message,
            properties,
            exception,
        )

    # =========================================================
    # Create Entry
    # =========================================================

    def _create_entry(
        self,
        level: LogLevel,
        message: str,
        properties: dict[str, Any] | None,
        exception: Exception | None,
    ) -> LogEntry:

        context = (
            LoggingContextAccessor.get()
        )

        request_id = None
        correlation_id = None
        ip_address = None
        user_id = None
        http_method = None
        path = None
        status_code = None

        if (
            context is not None
            and self._settings.include_request_context
        ):
            request_id = context.request_id
            correlation_id = context.correlation_id
            ip_address = context.ip_address
            http_method = context.http_method
            path = context.path
            status_code = context.status_code

        if (
            context is not None
            and self._settings.include_user_context
        ):
            user_id = context.user_id

        exception_type = None
        exception_message = None
        stack_trace = None

        if exception is not None:

            exception_type = type(
                exception
            ).__name__

            exception_message = str(
                exception
            )

            if self._settings.include_stack_trace:

                stack_trace = "".join(
                    traceback.format_exception(
                        type(exception),
                        exception,
                        exception.__traceback__,
                    )
                )

        return LogEntry(
            level=level,
            message=message,
            request_id=request_id,
            correlation_id=correlation_id,
            ip_address=ip_address,
            user_id=user_id,
            http_method=http_method,
            path=path,
            status_code=status_code,
            logger_name=self._logger_name,
            exception_type=exception_type,
            exception_message=exception_message,
            stack_trace=stack_trace,
            properties=properties or {},
        )

    # =========================================================
    # Console
    # =========================================================

    def _write_console(
        self,
        entry: LogEntry,
        exception: Exception | None,
    ) -> None:

        self._console_logger.log(
            int(entry.level),
            entry.message,
            exc_info=(
                (
                    type(exception),
                    exception,
                    exception.__traceback__,
                )
                if exception is not None
                else None
            ),
        )
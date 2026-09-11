import json
from pathlib import Path

from Configs.Loggings.logging_settings import (
    LoggingSettings,
)

from Core.Application.Contracts.Loggings.log_fallback_writer import (
    ILogFallbackWriter,
)

from Core.Domain.ViewModels.Loggings.log_entry import (
    LogEntry,
)


class FileLogFallbackWriter(
    ILogFallbackWriter,
):

    def __init__(
        self,
        settings: LoggingSettings,
    ) -> None:

        self._file_path = Path(
            settings.fallback_file_path
        )

    def write(
        self,
        entries: list[LogEntry],
    ) -> None:

        if not entries:
            return

        self._file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self._file_path.open(
            mode="a",
            encoding="utf-8",
        ) as file:

            for entry in entries:

                data = {
                    "timestamp": entry.timestamp.isoformat(),
                    "level": entry.level.name,
                    "message": entry.message,

                    "request_id": entry.request_id,
                    "correlation_id": entry.correlation_id,

                    "ip_address": entry.ip_address,
                    "user_id": entry.user_id,

                    "http_method": entry.http_method,
                    "path": entry.path,
                    "status_code": entry.status_code,

                    "logger_name": entry.logger_name,

                    "exception_type": entry.exception_type,
                    "exception_message": entry.exception_message,
                    "stack_trace": entry.stack_trace,

                    "properties": entry.properties,
                }

                file.write(
                    json.dumps(
                        data,
                        ensure_ascii=False,
                        default=str,
                    )
                )

                file.write(
                    "\n"
                )
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from Core.Domain.Enums.Loggings.log_level import (
    LogLevel,
)


@dataclass(
    slots=True,
)
class LogEntry:

    level: LogLevel

    message: str

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    request_id: str | None = None

    correlation_id: str | None = None

    ip_address: str | None = None

    user_id: int | None = None

    http_method: str | None = None

    path: str | None = None

    status_code: int | None = None

    logger_name: str | None = None

    exception_type: str | None = None

    exception_message: str | None = None

    stack_trace: str | None = None

    properties: dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )
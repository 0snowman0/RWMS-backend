from contextvars import (
    ContextVar,
    Token,
)
from dataclasses import dataclass


@dataclass(
    slots=True,
)
class LoggingContext:

    request_id: str | None = None

    correlation_id: str | None = None

    ip_address: str | None = None

    user_id: int | None = None

    http_method: str | None = None

    path: str | None = None

    status_code: int | None = None


_current_logging_context: ContextVar[
    LoggingContext | None
] = ContextVar(
    "current_logging_context",
    default=None,
)


class LoggingContextAccessor:

    @staticmethod
    def get() -> LoggingContext | None:

        return _current_logging_context.get()

    @staticmethod
    def set(
        context: LoggingContext,
    ) -> Token:

        return _current_logging_context.set(
            context
        )

    @staticmethod
    def reset(
        token: Token,
    ) -> None:

        _current_logging_context.reset(
            token
        )

    @staticmethod
    def clear() -> None:

        _current_logging_context.set(
            None
        )
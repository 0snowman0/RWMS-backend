from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from Core.Application.Contracts.Loggings.log_batch_writer import (
    ILogBatchWriter,
)



from Core.Domain.Models.Logs.log import Log
from Core.Domain.ViewModels.Loggings.log_entry import (
    LogEntry,
)


class PostgresLogBatchWriter(
    ILogBatchWriter,
):

    def __init__(
        self,
        session_factory: async_sessionmaker[
            AsyncSession
        ],
    ) -> None:

        self._session_factory = (
            session_factory
        )

    async def write(
        self,
        entries: list[LogEntry],
    ) -> None:

        if not entries:
            return

        logs = [
            Log(
                level=int(entry.level),
                message=entry.message,

                request_id=entry.request_id,
                correlation_id=entry.correlation_id,

                ip_address=entry.ip_address,
                user_id=entry.user_id,

                http_method=entry.http_method,
                path=entry.path,
                status_code=entry.status_code,

                logger_name=entry.logger_name,

                exception_type=entry.exception_type,
                exception_message=entry.exception_message,
                stack_trace=entry.stack_trace,

                properties=entry.properties,

                created_at=entry.timestamp,
            )
            for entry in entries
        ]

        async with self._session_factory() as session:

            try:

                session.add_all(
                    logs
                )

                await session.commit()

            except Exception:

                await session.rollback()

                raise
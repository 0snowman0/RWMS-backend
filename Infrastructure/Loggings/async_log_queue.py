import asyncio

from Configs.Loggings.logging_settings import (
    LoggingSettings,
)

from Core.Application.Contracts.Loggings.log_queue import (
    ILogQueue,
)
from Core.Domain.ViewModels.Loggings.log_entry import LogEntry



class AsyncLogQueue(
    ILogQueue,
):

    def __init__(
        self,
        settings: LoggingSettings,
    ) -> None:

        self._queue: asyncio.Queue[
            LogEntry
        ] = asyncio.Queue(
            maxsize=settings.max_queue_size
        )

    def enqueue(
        self,
        entry: LogEntry,
    ) -> bool:

        try:

            self._queue.put_nowait(
                entry
            )

            return True

        except asyncio.QueueFull:

            return False

    async def dequeue(
        self,
    ) -> LogEntry:

        return await self._queue.get()

    def task_done(
        self,
    ) -> None:

        self._queue.task_done()

    def size(
        self,
    ) -> int:

        return self._queue.qsize()
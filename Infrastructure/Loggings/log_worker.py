import asyncio

from Configs.Loggings.logging_settings import (
    LoggingSettings,
)

from Core.Application.Contracts.Loggings.log_batch_writer import (
    ILogBatchWriter,
)

from Core.Application.Contracts.Loggings.log_fallback_writer import (
    ILogFallbackWriter,
)

from Core.Application.Contracts.Loggings.log_queue import (
    ILogQueue,
)

from Core.Domain.ViewModels.Loggings.log_entry import (
    LogEntry,
)


class LogWorker:

    def __init__(
        self,
        log_queue: ILogQueue,
        batch_writer: ILogBatchWriter,
        fallback_writer: ILogFallbackWriter,
        settings: LoggingSettings,
    ) -> None:

        self._log_queue = log_queue
        self._batch_writer = batch_writer
        self._fallback_writer = fallback_writer
        self._settings = settings

        self._stop_event = asyncio.Event()

        self._task: asyncio.Task | None = None

    # =========================================================
    # Start
    # =========================================================

    async def start(
        self,
    ) -> None:

        if (
            self._task is not None
            and not self._task.done()
        ):
            return

        self._stop_event.clear()

        self._task = asyncio.create_task(
            self._run(),
            name="log-worker",
        )

    # =========================================================
    # Stop
    # =========================================================

    async def stop(
        self,
    ) -> None:

        if self._task is None:
            return

        self._stop_event.set()

        await self._task

        self._task = None

    # =========================================================
    # Worker Loop
    # =========================================================

    async def _run(
        self,
    ) -> None:

        batch: list[LogEntry] = []

        while not self._stop_event.is_set():

            timeout = (
                self._settings.flush_interval_seconds
                if batch
                else None
            )

            state, entry = await self._wait_for_entry(
                timeout=timeout,
            )

            # -------------------------
            # Log received
            # -------------------------

            if state == "entry":

                if entry is None:
                    continue

                batch.append(
                    entry
                )

                if (
                    len(batch)
                    >= self._settings.batch_size
                ):

                    await self._flush(
                        batch
                    )

                    batch.clear()

                continue

            # -------------------------
            # Flush interval reached
            # -------------------------

            if state == "timeout":

                if batch:

                    await self._flush(
                        batch
                    )

                    batch.clear()

                continue

            # -------------------------
            # Stop requested
            # -------------------------

            if state == "stop":
                break

        await self._flush_remaining(
            batch
        )

    # =========================================================
    # Wait Queue / Timer / Stop
    # =========================================================

    async def _wait_for_entry(
        self,
        timeout: float | None,
    ) -> tuple[
        str,
        LogEntry | None,
    ]:

        dequeue_task = asyncio.create_task(
            self._log_queue.dequeue()
        )

        stop_task = asyncio.create_task(
            self._stop_event.wait()
        )

        done, pending = await asyncio.wait(
            {
                dequeue_task,
                stop_task,
            },
            timeout=timeout,
            return_when=asyncio.FIRST_COMPLETED,
        )

        # -------------------------
        # Timeout
        # -------------------------

        if not done:

            await self._cancel_tasks(
                dequeue_task,
                stop_task,
            )

            return (
                "timeout",
                None,
            )

        # -------------------------
        # Log received
        # -------------------------

        if dequeue_task in done:

            entry = dequeue_task.result()

            if not stop_task.done():

                stop_task.cancel()

                await asyncio.gather(
                    stop_task,
                    return_exceptions=True,
                )

            return (
                "entry",
                entry,
            )

        # -------------------------
        # Stop
        # -------------------------

        if not dequeue_task.done():

            dequeue_task.cancel()

            await asyncio.gather(
                dequeue_task,
                return_exceptions=True,
            )

        return (
            "stop",
            None,
        )

    # =========================================================
    # Flush
    # =========================================================

    async def _flush(
        self,
        batch: list[LogEntry],
    ) -> None:

        entries = list(
            batch
        )

        try:

            await self._batch_writer.write(
                entries
            )

        except Exception:

            if self._settings.fallback_to_file:

                try:

                    await asyncio.to_thread(
                        self._fallback_writer.write,
                        entries,
                    )

                except Exception:
                    pass

        finally:

            for _ in entries:

                self._log_queue.task_done()

    # =========================================================
    # Shutdown Flush
    # =========================================================

    async def _flush_remaining(
        self,
        batch: list[LogEntry],
    ) -> None:

        while self._log_queue.size() > 0:

            entry = await self._log_queue.dequeue()

            batch.append(
                entry
            )

            if (
                len(batch)
                >= self._settings.batch_size
            ):

                await self._flush(
                    batch
                )

                batch.clear()

        if batch:

            await self._flush(
                batch
            )

            batch.clear()

    # =========================================================
    # Helpers
    # =========================================================

    async def _cancel_tasks(
        self,
        *tasks: asyncio.Task,
    ) -> None:

        for task in tasks:

            if not task.done():
                task.cancel()

        await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )
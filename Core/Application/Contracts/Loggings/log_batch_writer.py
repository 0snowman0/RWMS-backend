from abc import ABC, abstractmethod

from Core.Domain.ViewModels.Loggings.log_entry import LogEntry



class ILogBatchWriter(ABC):

    @abstractmethod
    async def write(
        self,
        entries: list[LogEntry],
    ) -> None:
        pass
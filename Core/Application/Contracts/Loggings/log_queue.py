from abc import ABC, abstractmethod

from Core.Domain.ViewModels.Loggings.log_entry import LogEntry



class ILogQueue(ABC):

    @abstractmethod
    def enqueue(
        self,
        entry: LogEntry,
    ) -> bool:
        pass

    @abstractmethod
    async def dequeue(
        self,
    ) -> LogEntry:
        pass

    @abstractmethod
    def task_done(
        self,
    ) -> None:
        pass

    @abstractmethod
    def size(
        self,
    ) -> int:
        pass
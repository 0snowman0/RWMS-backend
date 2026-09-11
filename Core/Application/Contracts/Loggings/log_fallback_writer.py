from abc import ABC, abstractmethod

from Core.Domain.ViewModels.Loggings.log_entry import (
    LogEntry,
)


class ILogFallbackWriter(ABC):

    @abstractmethod
    def write(
        self,
        entries: list[LogEntry],
    ) -> None:
        pass
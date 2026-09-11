from abc import ABC, abstractmethod
from typing import Any

from Core.Domain.Enums.Loggings.log_level import (
    LogLevel,
)


class ILogger(ABC):

    @abstractmethod
    def log(
        self,
        level: LogLevel,
        message: str,
        properties: dict[str, Any] | None = None,
        exception: Exception | None = None,
    ) -> None:
        pass

    @abstractmethod
    def debug(
        self,
        message: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        pass

    @abstractmethod
    def info(
        self,
        message: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        pass

    @abstractmethod
    def warning(
        self,
        message: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        pass

    @abstractmethod
    def error(
        self,
        message: str,
        properties: dict[str, Any] | None = None,
        exception: Exception | None = None,
    ) -> None:
        pass

    @abstractmethod
    def critical(
        self,
        message: str,
        properties: dict[str, Any] | None = None,
        exception: Exception | None = None,
    ) -> None:
        pass

    @abstractmethod
    def exception(
        self,
        message: str,
        exception: Exception,
        properties: dict[str, Any] | None = None,
    ) -> None:
        pass
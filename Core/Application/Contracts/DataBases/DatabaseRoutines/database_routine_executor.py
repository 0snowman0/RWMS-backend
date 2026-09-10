from abc import ABC, abstractmethod
from typing import Any, TypeVar


T = TypeVar("T")


class IDatabaseRoutineExecutor(ABC):

    @abstractmethod
    async def execute(
        self,
        name: str,
        params: dict[str, Any] | None = None,
    ) -> None:
        pass

    @abstractmethod
    async def execute_scalar(
        self,
        name: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        pass

    @abstractmethod
    async def execute_raw(
        self,
        name: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def execute_one(
        self,
        name: str,
        destination_type: type[T],
        params: dict[str, Any] | None = None,
    ) -> T | None:
        pass

    @abstractmethod
    async def execute_list(
        self,
        name: str,
        destination_type: type[T],
        params: dict[str, Any] | None = None,
    ) -> list[T]:
        pass

    @abstractmethod
    async def execute_multi(
        self,
        name: str,
        destination_types: tuple[type, ...],
        params: dict[str, Any] | None = None,
        result_count: int | None = None,
    ) -> tuple[list[Any], ...]:
        pass
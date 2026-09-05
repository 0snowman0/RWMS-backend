from abc import ABC, abstractmethod
from typing import Any, Iterable, TypeVar


TDestination = TypeVar("TDestination")


class IMapper(ABC):

    @abstractmethod
    def map(
        self,
        source: Any,
        destination_type: type[TDestination],
        *,
        ignore_none: bool = False,
        ignore_unset: bool = False,
    ) -> TDestination:
        pass

    @abstractmethod
    def map_list(
        self,
        source: Iterable[Any],
        destination_type: type[TDestination],
        *,
        ignore_none: bool = False,
        ignore_unset: bool = False,
    ) -> list[TDestination]:
        pass

    @abstractmethod
    def map_to(
        self,
        source: Any,
        destination: TDestination,
        *,
        ignore_none: bool = False,
        ignore_unset: bool = False,
    ) -> TDestination:
        pass
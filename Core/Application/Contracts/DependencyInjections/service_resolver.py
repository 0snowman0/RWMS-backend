from abc import ABC, abstractmethod
from typing import TypeVar


T = TypeVar("T")


class IServiceResolver(ABC):

    @abstractmethod
    def resolve(
        self,
        service_type: type[T],
    ) -> T:
        pass
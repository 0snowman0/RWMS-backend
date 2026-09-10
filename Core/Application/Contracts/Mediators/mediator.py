from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Generic, TypeVar


TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")


NextHandler = Callable[
    [],
    Awaitable[TResponse],
]


class IMediator(ABC):

    @abstractmethod
    async def send(
        self,
        request: TRequest,
    ) -> TResponse:
        pass


class IRequestHandler(
    ABC,
    Generic[TRequest, TResponse],
):

    @abstractmethod
    async def handle(
        self,
        request: TRequest,
    ) -> TResponse:
        pass


class IPipelineBehavior(
    ABC,
    Generic[TRequest, TResponse],
):

    @abstractmethod
    async def handle(
        self,
        request: TRequest,
        next_handler: NextHandler[TResponse],
    ) -> TResponse:
        pass
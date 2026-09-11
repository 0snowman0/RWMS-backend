from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Generic, TypeVar


TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")


# ============================================================
# Request
# ============================================================

class IRequest(
    ABC,
    Generic[TResponse],
):
    pass


# ============================================================
# Next Handler
# ============================================================

NextHandler = Callable[
    [],
    Awaitable[TResponse],
]


# ============================================================
# Mediator
# ============================================================

class IMediator(ABC):

    @abstractmethod
    async def send(
        self,
        request: IRequest[TResponse],
    ) -> TResponse:
        pass


# ============================================================
# Request Handler
# ============================================================

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


# ============================================================
# Pipeline Behavior
# ============================================================

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
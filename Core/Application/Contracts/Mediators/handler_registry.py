from abc import ABC, abstractmethod

from Core.Application.Contracts.Mediators.mediator import IRequestHandler



class IHandlerRegistry(ABC):

    @abstractmethod
    def register(
        self,
        request_type: type,
        handler_type: type[IRequestHandler],
    ) -> None:
        pass

    @abstractmethod
    def get_handler_type(
        self,
        request_type: type,
    ) -> type[IRequestHandler]:
        pass
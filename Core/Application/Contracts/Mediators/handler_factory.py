from abc import ABC, abstractmethod

from Core.Application.Contracts.Mediators.mediator import IRequestHandler



class IHandlerFactory(ABC):

    @abstractmethod
    def create(
        self,
        handler_type: type[IRequestHandler],
    ) -> IRequestHandler:
        pass
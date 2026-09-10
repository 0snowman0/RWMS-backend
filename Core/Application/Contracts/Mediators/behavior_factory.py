from abc import ABC, abstractmethod

from Core.Application.Contracts.Mediators.mediator import IPipelineBehavior


class IBehaviorFactory(ABC):

    @abstractmethod
    def create(
        self,
        behavior_class: type[IPipelineBehavior],
    ) -> IPipelineBehavior:
        pass
from abc import ABC, abstractmethod

from Core.Application.Contracts.Mediators.mediator import IPipelineBehavior
from Core.Domain.Enums.Mediators.mediator import BehaviorType



class IBehaviorRegistry(ABC):

    @abstractmethod
    def register(
        self,
        behavior_type: BehaviorType,
        behavior_class: type[IPipelineBehavior],
    ) -> None:
        pass

    @abstractmethod
    def get_behavior_class(
        self,
        behavior_type: BehaviorType,
    ) -> type[IPipelineBehavior]:
        pass
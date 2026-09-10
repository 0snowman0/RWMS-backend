
from Core.Application.Contracts.Mediators.behavior_registry import IBehaviorRegistry
from Core.Application.Contracts.Mediators.mediator import IPipelineBehavior
from Core.Domain.Enums.Mediators.mediator import BehaviorType


class BehaviorRegistry(IBehaviorRegistry):

    def __init__(self):
        self._behaviors: dict[
            BehaviorType,
            type[IPipelineBehavior],
        ] = {}

    def register(
        self,
        behavior_type: BehaviorType,
        behavior_class: type[IPipelineBehavior],
    ) -> None:

        if behavior_type in self._behaviors:
            raise ValueError(
                f"Behavior '{behavior_type.value}' "
                f"is already registered."
            )

        self._behaviors[
            behavior_type
        ] = behavior_class

    def get_behavior_class(
        self,
        behavior_type: BehaviorType,
    ) -> type[IPipelineBehavior]:

        behavior_class = self._behaviors.get(
            behavior_type
        )

        if behavior_class is None:
            raise KeyError(
                f"Behavior '{behavior_type.value}' "
                f"was not registered."
            )

        return behavior_class
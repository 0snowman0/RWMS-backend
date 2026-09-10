from typing import TypeVar

from Core.Domain.Enums.Mediators.mediator import BehaviorType



T = TypeVar("T")


BEHAVIOR_TYPE_ATTRIBUTE = "__mediator_behavior_type__"


def behavior(
    behavior_type: BehaviorType,
):
    def decorator(
        behavior_class: T,
    ) -> T:

        setattr(
            behavior_class,
            BEHAVIOR_TYPE_ATTRIBUTE,
            behavior_type,
        )

        return behavior_class

    return decorator
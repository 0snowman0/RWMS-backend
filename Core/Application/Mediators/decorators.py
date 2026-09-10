from typing import TypeVar

from Core.Domain.Enums.Mediators.mediator import BehaviorType, RequestType

T = TypeVar("T")


REQUEST_TYPE_ATTRIBUTE = "__mediator_request_type__"

SKIP_BEHAVIORS_ATTRIBUTE = "__mediator_skip_behaviors__"

REQUIRE_BEHAVIORS_ATTRIBUTE = "__mediator_require_behaviors__"


def request_type(
    value: RequestType,
):
    def decorator(cls: T) -> T:

        setattr(
            cls,
            REQUEST_TYPE_ATTRIBUTE,
            value,
        )

        return cls

    return decorator


def skip_behaviors(
    *behaviors: BehaviorType,
):
    def decorator(cls: T) -> T:

        current = set(
            getattr(
                cls,
                SKIP_BEHAVIORS_ATTRIBUTE,
                (),
            )
        )

        current.update(behaviors)

        setattr(
            cls,
            SKIP_BEHAVIORS_ATTRIBUTE,
            frozenset(current),
        )

        return cls

    return decorator


def require_behaviors(
    *behaviors: BehaviorType,
):
    def decorator(cls: T) -> T:

        current = set(
            getattr(
                cls,
                REQUIRE_BEHAVIORS_ATTRIBUTE,
                (),
            )
        )

        current.update(behaviors)

        setattr(
            cls,
            REQUIRE_BEHAVIORS_ATTRIBUTE,
            frozenset(current),
        )

        return cls

    return decorator
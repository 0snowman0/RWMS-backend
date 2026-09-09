from collections.abc import Callable
from typing import TypeVar


T = TypeVar("T", bound=Callable)

RATE_LIMIT_POLICY_ATTRIBUTE = "__rate_limit_policy__"


def rate_limit(policy_name: str):

    def decorator(func: T) -> T:

        setattr(
            func,
            RATE_LIMIT_POLICY_ATTRIBUTE,
            policy_name,
        )

        return func

    return decorator
from collections.abc import Callable

from Api.RateLimiting.decorators import RATE_LIMIT_POLICY_ATTRIBUTE
from Core.Application.Contracts.RateLimiting.rate_limit import (
    IRateLimitPolicyProvider,
)

from Core.Domain.ViewModels.RateLimiting.rate_limit import (
    RateLimitPolicy,
)

class RateLimitPolicyResolver:

    def __init__(
        self,
        policy_provider: IRateLimitPolicyProvider,
    ):
        self._policy_provider = policy_provider

    def resolve(
        self,
        endpoint: Callable,
    ) -> RateLimitPolicy:

        policy_name = getattr(
            endpoint,
            RATE_LIMIT_POLICY_ATTRIBUTE,
            None,
        )

        if policy_name is not None:
            return self._policy_provider.get_policy(
                policy_name
            )

        return self._policy_provider.get_default_policy()
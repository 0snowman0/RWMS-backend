from Core.Application.Contracts.RateLimiting.rate_limit import (
    IRateLimitPolicyProvider,
)
from Core.Domain.ViewModels.RateLimiting.rate_limit import RateLimitPolicy


class RateLimitPolicyProvider(IRateLimitPolicyProvider):

    def __init__(
        self,
        default_policy: RateLimitPolicy,
        policies: dict[str, RateLimitPolicy],
    ):
        self._default_policy = default_policy
        self._policies = policies

    def get_default_policy(self) -> RateLimitPolicy:
        return self._default_policy

    def get_policy(
        self,
        name: str,
    ) -> RateLimitPolicy:

        policy = self._policies.get(name)

        if policy is None:
            raise KeyError(
                f"Rate limit policy '{name}' was not found."
            )

        return policy
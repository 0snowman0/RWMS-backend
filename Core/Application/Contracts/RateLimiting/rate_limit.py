from abc import ABC, abstractmethod

from Core.Domain.ViewModels.RateLimiting.rate_limit import RateLimitPolicy, RateLimitResult


class IRateLimiter(ABC):

    @abstractmethod
    async def acquire(
        self,
        key: str,
        policy: RateLimitPolicy,
    ) -> RateLimitResult:
        pass


class IRateLimitPolicyProvider(ABC):

    @abstractmethod
    def get_default_policy(self) -> RateLimitPolicy:
        pass

    @abstractmethod
    def get_policy(
        self,
        name: str,
    ) -> RateLimitPolicy:
        pass
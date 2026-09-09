from abc import ABC, abstractmethod

from Core.Application.Contracts.RateLimiting.rate_limit import (
    IRateLimiter,
)

from Core.Domain.ViewModels.RateLimiting.rate_limit import (
    RateLimitPolicy,
)


class IRateLimiterResolver(ABC):

    @abstractmethod
    def resolve(
        self,
        policy: RateLimitPolicy,
    ) -> IRateLimiter:
        pass
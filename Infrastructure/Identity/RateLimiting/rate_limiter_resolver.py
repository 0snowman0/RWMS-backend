from Core.Application.Contracts.RateLimiting.rate_limit import (
    IRateLimiter,
)

from Core.Application.Contracts.RateLimiting.rate_limiter_resolver import (
    IRateLimiterResolver,
)

from Core.Domain.ViewModels.RateLimiting.rate_limit import (
    FixedWindowOptions,
    SlidingWindowOptions,
    TokenBucketOptions,
    RateLimitPolicy,
)


class RateLimiterResolver(IRateLimiterResolver):

    def __init__(
        self,
        fixed_window: IRateLimiter,
        sliding_window: IRateLimiter,
        token_bucket: IRateLimiter,
    ):
        self._fixed_window = fixed_window
        self._sliding_window = sliding_window
        self._token_bucket = token_bucket

    def resolve(
        self,
        policy: RateLimitPolicy,
    ) -> IRateLimiter:

        options = policy.options

        if isinstance(
            options,
            FixedWindowOptions,
        ):
            return self._fixed_window

        if isinstance(
            options,
            SlidingWindowOptions,
        ):
            return self._sliding_window

        if isinstance(
            options,
            TokenBucketOptions,
        ):
            return self._token_bucket

        raise TypeError(
            f"Unsupported rate limit options: "
            f"{type(options).__name__}"
        )
from fastapi import FastAPI

from Configs.RateLimiting.rate_limit import (
    DEFAULT_RATE_LIMIT_POLICY,
    RATE_LIMIT_POLICIES,
)
from Infrastructure.Identity.RateLimiting.Strategies.fixed_window_rate_limiter import FixedWindowRateLimiter
from Infrastructure.Identity.RateLimiting.Strategies.sliding_window_rate_limiter import SlidingWindowRateLimiter
from Infrastructure.Identity.RateLimiting.Strategies.token_bucket_rate_limiter import TokenBucketRateLimiter
from Infrastructure.Identity.RateLimiting.policy_provider import RateLimitPolicyProvider
from Infrastructure.Identity.RateLimiting.rate_limiter_resolver import RateLimiterResolver


def configure_rate_limiting(
    app: FastAPI,
) -> None:

    policy_provider = RateLimitPolicyProvider(
        default_policy=DEFAULT_RATE_LIMIT_POLICY,
        policies=RATE_LIMIT_POLICIES,
    )

    fixed_window = FixedWindowRateLimiter()

    sliding_window = SlidingWindowRateLimiter()

    token_bucket = TokenBucketRateLimiter()

    limiter_resolver = RateLimiterResolver(
        fixed_window=fixed_window,
        sliding_window=sliding_window,
        token_bucket=token_bucket,
    )

    app.state.rate_limit_policy_provider = (
        policy_provider
    )

    app.state.rate_limiter_resolver = (
        limiter_resolver
    )
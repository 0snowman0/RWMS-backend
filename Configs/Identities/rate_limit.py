from datetime import timedelta
from Core.Domain.ViewModels.RateLimiting.rate_limit import FixedWindowOptions, RateLimitPolicy


DEFAULT_RATE_LIMIT_POLICY = RateLimitPolicy(
    name="default",
    options=FixedWindowOptions(
        permit_limit=100,
        window=timedelta(minutes=1),
    ),
)


RATE_LIMIT_POLICIES: dict[str, RateLimitPolicy] = {

    "login": RateLimitPolicy(
        name="login",
        options=FixedWindowOptions(
            permit_limit=5,
            window=timedelta(minutes=1),
        ),
    ),

    "refresh_token": RateLimitPolicy(
        name="refresh_token",
        options=FixedWindowOptions(
            permit_limit=10,
            window=timedelta(minutes=1),
        ),
    ),

    "register": RateLimitPolicy(
        name="register",
        options=FixedWindowOptions(
            permit_limit=3,
            window=timedelta(minutes=1),
        ),
    ),
}
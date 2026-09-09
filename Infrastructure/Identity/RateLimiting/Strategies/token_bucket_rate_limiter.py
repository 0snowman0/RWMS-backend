import asyncio
import math
import time
from dataclasses import dataclass

from Core.Application.Contracts.RateLimiting.rate_limit import (
    IRateLimiter,
)

from Core.Domain.ViewModels.RateLimiting.rate_limit import (
    RateLimitPolicy,
    RateLimitResult,
    TokenBucketOptions,
)


@dataclass
class TokenBucketState:
    tokens: int
    last_replenishment: float


class TokenBucketRateLimiter(IRateLimiter):

    def __init__(self):
        self._storage: dict[
            tuple[str, str],
            TokenBucketState
        ] = {}

        self._lock = asyncio.Lock()

    async def acquire(
        self,
        key: str,
        policy: RateLimitPolicy,
    ) -> RateLimitResult:

        options = policy.options

        if not isinstance(
            options,
            TokenBucketOptions,
        ):
            raise TypeError(
                "TokenBucketRateLimiter only supports "
                "TokenBucketOptions"
            )

        storage_key = (
            policy.name,
            key,
        )

        now = time.monotonic()

        replenishment_seconds = (
            options.replenishment_period
            .total_seconds()
        )

        async with self._lock:

            state = self._storage.get(
                storage_key
            )

            if state is None:

                state = TokenBucketState(
                    tokens=options.token_limit,
                    last_replenishment=now,
                )

                self._storage[
                    storage_key
                ] = state

            elapsed = (
                now
                - state.last_replenishment
            )

            periods = int(
                elapsed
                // replenishment_seconds
            )

            if periods > 0:

                tokens_to_add = (
                    periods
                    * options.tokens_per_period
                )

                state.tokens = min(
                    options.token_limit,
                    state.tokens
                    + tokens_to_add,
                )

                state.last_replenishment += (
                    periods
                    * replenishment_seconds
                )

            if state.tokens <= 0:

                elapsed_since_replenishment = (
                    now
                    - state.last_replenishment
                )

                retry_after = math.ceil(
                    replenishment_seconds
                    - elapsed_since_replenishment
                )

                return RateLimitResult(
                    is_allowed=False,
                    limit=options.token_limit,
                    remaining=0,
                    retry_after_seconds=max(
                        1,
                        retry_after,
                    ),
                )

            state.tokens -= 1

            return RateLimitResult(
                is_allowed=True,
                limit=options.token_limit,
                remaining=state.tokens,
                retry_after_seconds=None,
            )
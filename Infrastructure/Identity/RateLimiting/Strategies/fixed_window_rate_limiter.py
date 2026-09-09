import asyncio
import math
import time
from dataclasses import dataclass

from Core.Application.Contracts.RateLimiting.rate_limit import (
    IRateLimiter,
)

from Core.Domain.ViewModels.RateLimiting.rate_limit import (
    FixedWindowOptions,
    RateLimitPolicy,
    RateLimitResult,
)


@dataclass
class FixedWindowState:
    count: int
    started_at: float


class FixedWindowRateLimiter(IRateLimiter):

    def __init__(self):
        self._storage: dict[
            tuple[str, str],
            FixedWindowState
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
            FixedWindowOptions,
        ):
            raise TypeError(
                "FixedWindowRateLimiter only supports "
                "FixedWindowOptions"
            )

        storage_key = (
            policy.name,
            key,
        )

        now = time.monotonic()

        window_seconds = (
            options.window.total_seconds()
        )

        async with self._lock:

            state = self._storage.get(
                storage_key
            )

            if (
                state is None
                or now - state.started_at
                >= window_seconds
            ):
                state = FixedWindowState(
                    count=0,
                    started_at=now,
                )

                self._storage[
                    storage_key
                ] = state

            if (
                state.count
                >= options.permit_limit
            ):

                elapsed = (
                    now - state.started_at
                )

                retry_after = math.ceil(
                    window_seconds - elapsed
                )

                return RateLimitResult(
                    is_allowed=False,
                    limit=options.permit_limit,
                    remaining=0,
                    retry_after_seconds=max(
                        0,
                        retry_after,
                    ),
                )

            state.count += 1

            remaining = (
                options.permit_limit
                - state.count
            )

            return RateLimitResult(
                is_allowed=True,
                limit=options.permit_limit,
                remaining=remaining,
                retry_after_seconds=None,
            )
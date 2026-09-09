import asyncio
import math
import time
from collections import deque
from dataclasses import dataclass

from Core.Application.Contracts.RateLimiting.rate_limit import (
    IRateLimiter,
)

from Core.Domain.ViewModels.RateLimiting.rate_limit import (
    RateLimitPolicy,
    RateLimitResult,
    SlidingWindowOptions,
)


@dataclass
class SlidingWindowSegment:
    started_at: float
    count: int


class SlidingWindowRateLimiter(IRateLimiter):

    def __init__(self):
        self._storage: dict[
            tuple[str, str],
            deque[SlidingWindowSegment]
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
            SlidingWindowOptions,
        ):
            raise TypeError(
                "SlidingWindowRateLimiter only supports "
                "SlidingWindowOptions"
            )

        storage_key = (
            policy.name,
            key,
        )

        now = time.monotonic()

        window_seconds = (
            options.window.total_seconds()
        )

        segment_seconds = (
            window_seconds
            / options.segments_per_window
        )

        current_segment_start = (
            math.floor(
                now / segment_seconds
            )
            * segment_seconds
        )

        window_start = (
            current_segment_start
            - window_seconds
            + segment_seconds
        )

        async with self._lock:

            segments = self._storage.get(
                storage_key
            )

            if segments is None:
                segments = deque()

                self._storage[
                    storage_key
                ] = segments

            while (
                segments
                and segments[0].started_at
                < window_start
            ):
                segments.popleft()

            total_requests = sum(
                segment.count
                for segment in segments
            )

            if (
                total_requests
                >= options.permit_limit
            ):

                oldest_segment = segments[0]

                retry_after = math.ceil(
                    (
                        oldest_segment.started_at
                        + window_seconds
                    )
                    - now
                )

                return RateLimitResult(
                    is_allowed=False,
                    limit=options.permit_limit,
                    remaining=0,
                    retry_after_seconds=max(
                        1,
                        retry_after,
                    ),
                )

            if (
                segments
                and segments[-1].started_at
                == current_segment_start
            ):

                segments[-1].count += 1

            else:

                segments.append(
                    SlidingWindowSegment(
                        started_at=current_segment_start,
                        count=1,
                    )
                )

            total_requests += 1

            remaining = max(
                0,
                options.permit_limit
                - total_requests,
            )

            return RateLimitResult(
                is_allowed=True,
                limit=options.permit_limit,
                remaining=remaining,
                retry_after_seconds=None,
            )
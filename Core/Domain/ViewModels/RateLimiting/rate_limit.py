from abc import ABC
from dataclasses import dataclass
from datetime import timedelta


# =========================================
# Options
# =========================================

@dataclass(frozen=True, slots=True)
class RateLimitOptions(ABC):
    pass


@dataclass(frozen=True, slots=True)
class FixedWindowOptions(RateLimitOptions):
    permit_limit: int
    window: timedelta

    def __post_init__(self):
        if self.permit_limit <= 0:
            raise ValueError("permit_limit must be greater than zero")

        if self.window.total_seconds() <= 0:
            raise ValueError("window must be greater than zero")


@dataclass(frozen=True, slots=True)
class SlidingWindowOptions(RateLimitOptions):
    permit_limit: int
    window: timedelta
    segments_per_window: int

    def __post_init__(self):
        if self.permit_limit <= 0:
            raise ValueError("permit_limit must be greater than zero")

        if self.window.total_seconds() <= 0:
            raise ValueError("window must be greater than zero")

        if self.segments_per_window <= 0:
            raise ValueError("segments_per_window must be greater than zero")


@dataclass(frozen=True, slots=True)
class TokenBucketOptions(RateLimitOptions):
    token_limit: int
    tokens_per_period: int
    replenishment_period: timedelta

    def __post_init__(self):
        if self.token_limit <= 0:
            raise ValueError("token_limit must be greater than zero")

        if self.tokens_per_period <= 0:
            raise ValueError("tokens_per_period must be greater than zero")

        if self.replenishment_period.total_seconds() <= 0:
            raise ValueError(
                "replenishment_period must be greater than zero"
            )


# =========================================
# Policy
# =========================================

@dataclass(frozen=True, slots=True)
class RateLimitPolicy:
    name: str
    options: RateLimitOptions


# =========================================
# Result
# =========================================

@dataclass(frozen=True, slots=True)
class RateLimitResult:
    is_allowed: bool

    limit: int
    remaining: int

    retry_after_seconds: int | None = None
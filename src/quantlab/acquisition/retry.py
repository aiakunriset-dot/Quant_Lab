from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Bounded exponential-backoff retry policy."""

    attempts: int = 5
    base_delay: float = 1.0
    max_delay: float = 30.0

    def __post_init__(self) -> None:
        if self.attempts < 1:
            raise ValueError("attempts must be >= 1")
        if self.base_delay < 0:
            raise ValueError("base_delay must be >= 0")
        if self.max_delay < self.base_delay:
            raise ValueError("max_delay must be >= base_delay")


def is_retryable_status(status_code: int) -> bool:
    """Return whether an HTTP status represents a transient acquisition failure."""
    return status_code == 429 or 500 <= status_code <= 599


def backoff_seconds(policy: RetryPolicy, retry_number: int) -> float:
    """Calculate bounded exponential backoff for a zero-based retry number."""
    if retry_number < 0:
        raise ValueError("retry_number must be >= 0")
    if retry_number == 0:
        return 0.0
    return min(policy.max_delay, policy.base_delay * (2 ** (retry_number - 1)))

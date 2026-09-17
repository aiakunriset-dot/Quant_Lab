from __future__ import annotations

from dataclasses import dataclass

import pytest

from quantlab.acquisition.retry import RetryPolicy, backoff_seconds, is_retryable_status


def test_429_is_retryable():
    assert is_retryable_status(429)


def test_503_is_retryable():
    assert is_retryable_status(503)


def test_404_is_not_retryable():
    assert not is_retryable_status(404)


def test_backoff_is_bounded():
    policy = RetryPolicy(attempts=5, base_delay=2.0, max_delay=5.0)
    assert backoff_seconds(policy, 0) == 0.0
    assert backoff_seconds(policy, 1) == 2.0
    assert backoff_seconds(policy, 2) == 4.0
    assert backoff_seconds(policy, 3) == 5.0


def test_invalid_retry_policy_is_rejected():
    with pytest.raises(ValueError):
        RetryPolicy(attempts=0, base_delay=1.0, max_delay=2.0)

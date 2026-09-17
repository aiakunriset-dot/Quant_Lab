from datetime import datetime, timezone

import pytest

from quantlab.acquisition.canonical import M1Bar
from quantlab.acquisition.validation import validate_m1_bars


def bar(minute: int, open_: float = 10, high: float = 12, low: float = 8, close: float = 11) -> M1Bar:
    return M1Bar(datetime(2024, 1, 2, 0, minute, tzinfo=timezone.utc), open_, high, low, close, 1.0)


def test_valid_bar_passes():
    assert validate_m1_bars((bar(0),)) == ()


def test_high_below_open_fails():
    with pytest.raises(ValueError):
        validate_m1_bars((bar(0, open_=13),))


def test_low_above_close_fails():
    with pytest.raises(ValueError):
        validate_m1_bars((bar(0, low=12),))


def test_duplicate_timestamp_fails():
    with pytest.raises(ValueError):
        validate_m1_bars((bar(0), bar(0)))


def test_non_monotonic_timestamp_fails():
    with pytest.raises(ValueError):
        validate_m1_bars((bar(1), bar(0)))

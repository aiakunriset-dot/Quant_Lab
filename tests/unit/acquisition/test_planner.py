from datetime import datetime, timezone

import pytest

from quantlab.acquisition.planner import build_plan, dukascopy_url, validate_instrument


def test_zero_based_month_url():
    dt = datetime(2024, 1, 15, 3, tzinfo=timezone.utc)
    assert dukascopy_url("usa500idxusd", dt).endswith("/2024/00/15/03h_ticks.bi5")


def test_interval_is_start_inclusive_end_exclusive():
    plan = build_plan("usa500idxusd", datetime(2024, 1, 1, tzinfo=timezone.utc), datetime(2024, 1, 1, 3, tzinfo=timezone.utc))
    assert [x.timestamp for x in plan] == [
        datetime(2024, 1, 1, 0, tzinfo=timezone.utc),
        datetime(2024, 1, 1, 1, tzinfo=timezone.utc),
        datetime(2024, 1, 1, 2, tzinfo=timezone.utc),
    ]


def test_naive_datetimes_are_rejected():
    with pytest.raises(ValueError):
        build_plan("usa500idxusd", datetime(2024, 1, 1), datetime(2024, 1, 2))


def test_invalid_instrument_is_rejected():
    with pytest.raises(ValueError):
        validate_instrument("NOT_A_SYMBOL")


def test_plan_is_deterministic():
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end = datetime(2024, 1, 1, 2, tzinfo=timezone.utc)
    assert build_plan("usa500idxusd", start, end) == build_plan("usa500idxusd", start, end)

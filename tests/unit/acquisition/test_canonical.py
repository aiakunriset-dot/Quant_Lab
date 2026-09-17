from datetime import datetime, timezone

import pytest

from quantlab.acquisition.canonical import aggregate_m1
from quantlab.acquisition.contracts import Tick


def tick(sec: int, bid: float, ask: float, bv: float = 1.0, av: float = 2.0) -> Tick:
    minute, second = divmod(sec, 60)
    return Tick(datetime(2024, 1, 2, 0, minute, second, tzinfo=timezone.utc), ask, bid, av, bv)


def test_single_minute_ohlc():
    bars = aggregate_m1((tick(1, 10, 11), tick(30, 8, 9), tick(59, 12, 13)))
    assert len(bars) == 1
    bar = bars[0]
    assert (bar.open, bar.high, bar.low, bar.close) == (10, 12, 8, 12)
    assert bar.volume == pytest.approx(9.0)


def test_two_minutes_are_separate():
    bars = aggregate_m1((tick(1, 10, 11), tick(61, 8, 9)))
    assert [b.timestamp.second for b in bars] == [0, 0]
    assert [b.timestamp.minute for b in bars] == [0, 1]


def test_empty_ticks_return_empty():
    assert aggregate_m1(()) == ()


def test_unsorted_ticks_are_rejected():
    with pytest.raises(ValueError):
        aggregate_m1((tick(30, 10, 11), tick(1, 8, 9)))


def test_invalid_bid_ask_is_rejected():
    with pytest.raises(ValueError):
        aggregate_m1((tick(1, 10, 9),))

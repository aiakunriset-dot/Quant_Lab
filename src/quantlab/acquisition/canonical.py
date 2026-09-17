from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .contracts import Tick


@dataclass(frozen=True, slots=True)
class M1Bar:
    """Canonical one-minute bid OHLCV bar."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


def aggregate_m1(ticks: tuple[Tick, ...]) -> tuple[M1Bar, ...]:
    """Aggregate ordered ticks into deterministic UTC one-minute bid bars."""
    if not ticks:
        return ()
    bars: list[M1Bar] = []
    current_minute: datetime | None = None
    open_price = high = low = close = volume = 0.0
    previous: datetime | None = None
    for tick in ticks:
        if tick.timestamp.tzinfo is None or tick.timestamp.utcoffset() is None:
            raise ValueError("tick timestamp must be timezone-aware")
        timestamp = tick.timestamp.astimezone(timezone.utc)
        if previous is not None and timestamp < previous:
            raise ValueError("ticks must be sorted ascending")
        if tick.ask < tick.bid:
            raise ValueError("ask must be >= bid")
        minute = timestamp.replace(second=0, microsecond=0)
        if current_minute is None or minute != current_minute:
            if current_minute is not None:
                bars.append(M1Bar(current_minute, open_price, high, low, close, volume))
            current_minute = minute
            open_price = high = low = close = tick.bid
            volume = tick.bid_volume + tick.ask_volume
        else:
            high = max(high, tick.bid)
            low = min(low, tick.bid)
            close = tick.bid
            volume += tick.bid_volume + tick.ask_volume
        previous = timestamp
    assert current_minute is not None
    bars.append(M1Bar(current_minute, open_price, high, low, close, volume))
    return tuple(bars)

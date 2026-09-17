from __future__ import annotations

from .canonical import M1Bar


def validate_m1_bars(bars: tuple[M1Bar, ...]) -> tuple[str, ...]:
    """Validate canonical M1 invariants and return non-fatal informational findings."""
    findings: list[str] = []
    previous = None
    for bar in bars:
        if bar.high < max(bar.open, bar.close):
            raise ValueError(f"high invariant violated at {bar.timestamp.isoformat()}")
        if bar.low > min(bar.open, bar.close):
            raise ValueError(f"low invariant violated at {bar.timestamp.isoformat()}")
        if bar.high < bar.low:
            raise ValueError(f"high/low ordering violated at {bar.timestamp.isoformat()}")
        if bar.volume < 0:
            raise ValueError(f"negative volume at {bar.timestamp.isoformat()}")
        if previous is not None and bar.timestamp <= previous:
            raise ValueError(f"non-monotonic or duplicate timestamp at {bar.timestamp.isoformat()}")
        previous = bar.timestamp
    return tuple(findings)

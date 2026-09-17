from __future__ import annotations

from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from .contracts import AcquisitionRequest, DownloadChunk

APPROVED_INSTRUMENTS = frozenset(
    {
        "usa30idxusd",
        "usa500idxusd",
        "usatechidxusd",
        "deuidxeur",
        "gbridxgbp",
        "jpnidxjpy",
        "xauusd",
        "dollaridxusd",
        "volidxusd",
    }
)


def validate_instrument(instrument: str) -> str:
    """Validate and normalize an approved Dukascopy instrument identifier."""
    normalized = instrument.strip().lower()
    if normalized not in APPROVED_INSTRUMENTS:
        raise ValueError(f"Unsupported instrument: {instrument!r}")
    return normalized


def _require_utc(value: datetime, name: str) -> datetime:
    """Require an aware UTC datetime and normalize its timezone object."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware UTC")
    normalized = value.astimezone(timezone.utc)
    return normalized


def dukascopy_url(instrument: str, timestamp: datetime) -> str:
    """Build the verified Dukascopy hourly tick endpoint with zero-based month."""
    symbol = quote(validate_instrument(instrument).upper(), safe="")
    ts = _require_utc(timestamp, "timestamp")
    return (
        "https://www.dukascopy.com/datafeed/"
        f"{symbol}/{ts.year:04d}/{ts.month - 1:02d}/{ts.day:02d}/{ts.hour:02d}h_ticks.bi5"
    )


def build_plan(instrument: str, start: datetime, end: datetime) -> tuple[DownloadChunk, ...]:
    """Build deterministic hourly chunks for the half-open UTC interval ``[start, end)``."""
    symbol = validate_instrument(instrument)
    start_utc = _require_utc(start, "start")
    end_utc = _require_utc(end, "end")
    if end_utc <= start_utc:
        raise ValueError("end must be later than start")
    cursor = start_utc.replace(minute=0, second=0, microsecond=0)
    chunks: list[DownloadChunk] = []
    while cursor < end_utc:
        chunks.append(DownloadChunk(symbol, cursor, dukascopy_url(symbol, cursor)))
        cursor += timedelta(hours=1)
    return tuple(chunks)


def build_request(instrument: str, start: datetime, end: datetime) -> AcquisitionRequest:
    """Create a validated immutable acquisition request."""
    symbol = validate_instrument(instrument)
    start_utc = _require_utc(start, "start")
    end_utc = _require_utc(end, "end")
    if end_utc <= start_utc:
        raise ValueError("end must be later than start")
    return AcquisitionRequest(symbol, start_utc, end_utc)

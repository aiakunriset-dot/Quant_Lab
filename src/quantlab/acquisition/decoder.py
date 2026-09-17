from __future__ import annotations

import lzma
import struct
from datetime import datetime, timedelta, timezone

from .contracts import Tick

RECORD_SIZE = 20
_RECORD = struct.Struct(">IIIff")


def decode_bi5(payload: bytes, day_start: datetime, price_scale: int) -> tuple[Tick, ...]:
    """Decode a Dukascopy 20-byte tick stream into UTC canonical ticks."""
    if not payload:
        raise ValueError("empty .bi5 payload")
    if price_scale <= 0:
        raise ValueError("price_scale must be > 0")
    if day_start.tzinfo is None or day_start.utcoffset() is None:
        raise ValueError("day_start must be timezone-aware")
    day_start = day_start.astimezone(timezone.utc)
    try:
        raw = lzma.decompress(payload)
    except lzma.LZMAError as exc:
        raise ValueError("invalid LZMA .bi5 payload") from exc
    if len(raw) == 0 or len(raw) % RECORD_SIZE != 0:
        raise ValueError(f"decoded payload size {len(raw)} is not a multiple of {RECORD_SIZE}")
    ticks: list[Tick] = []
    previous: datetime | None = None
    for offset in range(0, len(raw), RECORD_SIZE):
        milliseconds, ask_raw, bid_raw, ask_volume, bid_volume = _RECORD.unpack_from(raw, offset)
        timestamp = day_start + timedelta(milliseconds=milliseconds)
        if previous is not None and timestamp < previous:
            raise ValueError("decoded tick timestamps are not monotonic")
        ticks.append(
            Tick(
                timestamp=timestamp,
                ask=ask_raw / price_scale,
                bid=bid_raw / price_scale,
                ask_volume=float(ask_volume),
                bid_volume=float(bid_volume),
            )
        )
        previous = timestamp
    return tuple(ticks)

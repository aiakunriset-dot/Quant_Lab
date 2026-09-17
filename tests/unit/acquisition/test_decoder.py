from __future__ import annotations

import lzma
import struct
from datetime import datetime, timezone

import pytest

from quantlab.acquisition.decoder import decode_bi5


def _payload(records: list[tuple[int, int, int, float, float]]) -> bytes:
    raw = b"".join(struct.pack(">IIIff", *record) for record in records)
    return lzma.compress(raw, format=lzma.FORMAT_ALONE)


def test_decode_valid_record():
    day = datetime(2024, 1, 2, tzinfo=timezone.utc)
    data = _payload([(1000, 123450, 123400, 1.5, 2.5)])
    ticks = decode_bi5(data, day, price_scale=100000)
    assert len(ticks) == 1
    assert ticks[0].bid == pytest.approx(1.234)
    assert ticks[0].ask == pytest.approx(1.2345)
    assert ticks[0].timestamp == datetime(2024, 1, 2, 0, 0, 1, tzinfo=timezone.utc)


def test_decode_multiple_records_preserves_order():
    day = datetime(2024, 1, 2, tzinfo=timezone.utc)
    data = _payload([(1000, 100, 90, 1.0, 2.0), (2000, 110, 100, 1.0, 2.0)])
    ticks = decode_bi5(data, day, price_scale=100)
    assert [tick.bid for tick in ticks] == [0.9, 1.0]


def test_truncated_record_is_rejected():
    day = datetime(2024, 1, 2, tzinfo=timezone.utc)
    data = _payload([(1000, 100, 90, 1.0, 2.0)])[:-1]
    with pytest.raises(ValueError):
        decode_bi5(data, day, price_scale=100)


def test_empty_payload_is_rejected():
    day = datetime(2024, 1, 2, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        decode_bi5(b"", day, price_scale=100)


def test_invalid_price_scale_is_rejected():
    day = datetime(2024, 1, 2, tzinfo=timezone.utc)
    data = _payload([(1000, 100, 90, 1.0, 2.0)])
    with pytest.raises(ValueError):
        decode_bi5(data, day, price_scale=0)

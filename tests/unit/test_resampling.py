import polars as pl

from quantlab.data.resampling import resample_m1_to_m15


def test_m1_to_m15_aggregation() -> None:
    """Use first/max/min/last/sum aggregation semantics."""
    timestamps = pl.datetime_range(
        start=pl.datetime(2026, 1, 1, 0, 0),
        end=pl.datetime(2026, 1, 1, 0, 14),
        interval="1m",
        eager=True,
    )
    frame = pl.DataFrame({
        "timestamp": timestamps,
        "open": [100.0] + [101.0] * 14,
        "high": [100.0 + i for i in range(15)],
        "low": [100.0 - i * 0.1 for i in range(15)],
        "close": [101.0] * 14 + [110.0],
        "volume": [1.0] * 15,
    })
    result = resample_m1_to_m15(frame)
    assert result.height == 1
    assert result["open"][0] == 100.0
    assert result["high"][0] == 114.0
    assert result["low"][0] == 98.6
    assert result["close"][0] == 110.0
    assert result["volume"][0] == 15.0
    assert result["source_bar_count"][0] == 15

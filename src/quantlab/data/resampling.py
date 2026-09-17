import polars as pl

from quantlab.core.errors import DataIntegrityError


def resample_m1_to_m15(frame: pl.DataFrame) -> pl.DataFrame:
    """Aggregate canonical M1 OHLCV into deterministic M15 buckets."""
    required = {"timestamp", "open", "high", "low", "close", "volume"}
    missing = required.difference(frame.columns)
    if missing:
        raise DataIntegrityError(f"Missing columns: {sorted(missing)}")
    return (
        frame.sort("timestamp")
        .group_by_dynamic(
            "timestamp",
            every="15m",
            period="15m",
            closed="left",
            label="left",
        )
        .agg(
            pl.col("open").first(),
            pl.col("high").max(),
            pl.col("low").min(),
            pl.col("close").last(),
            pl.col("volume").sum(),
            pl.len().alias("source_bar_count"),
        )
        .sort("timestamp")
    )

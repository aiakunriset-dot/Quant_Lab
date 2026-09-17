import polars as pl

from quantlab.core.errors import DataIntegrityError
from quantlab.data.schema import REQUIRED_OHLCV_COLUMNS


def validate_ohlcv_frame(frame: pl.DataFrame) -> None:
    """Validate OHLCV structure and invariants without modifying the frame."""
    missing = [c for c in REQUIRED_OHLCV_COLUMNS if c not in frame.columns]
    if missing:
        raise DataIntegrityError(f"Missing required columns: {missing}")
    if frame.is_empty():
        raise DataIntegrityError("Dataset is empty")
    nulls = frame.select(pl.col(REQUIRED_OHLCV_COLUMNS).null_count()).row(0)
    if any(value > 0 for value in nulls):
        raise DataIntegrityError(f"Null values detected: {nulls}")
    invalid = frame.filter(
        (pl.col("open") <= 0)
        | (pl.col("high") <= 0)
        | (pl.col("low") <= 0)
        | (pl.col("close") <= 0)
        | (pl.col("high") < pl.max_horizontal("open", "close", "low"))
        | (pl.col("low") > pl.min_horizontal("open", "close", "high"))
        | (pl.col("volume") < 0)
    )
    if not invalid.is_empty():
        raise DataIntegrityError(
            f"OHLCV invariant violations detected: {invalid.height} rows"
        )

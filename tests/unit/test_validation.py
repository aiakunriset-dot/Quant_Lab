import polars as pl
import pytest

from quantlab.core.errors import DataIntegrityError
from quantlab.data.validation import validate_ohlcv_frame


def test_valid_ohlcv_passes() -> None:
    """Accept structurally valid OHLCV."""
    frame = pl.DataFrame({
        "timestamp": [1],
        "open": [100.0],
        "high": [105.0],
        "low": [95.0],
        "close": [102.0],
        "volume": [10.0],
    })
    validate_ohlcv_frame(frame)


def test_non_positive_price_fails() -> None:
    """Reject non-positive prices."""
    frame = pl.DataFrame({
        "timestamp": [1],
        "open": [0.0],
        "high": [105.0],
        "low": [95.0],
        "close": [102.0],
        "volume": [10.0],
    })
    with pytest.raises(DataIntegrityError):
        validate_ohlcv_frame(frame)

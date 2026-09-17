from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetIdentity:
    """Immutable identity for a published dataset."""

    dataset_id: str
    version: str
    symbol: str
    timeframe: str
    source: str
    content_sha256: str

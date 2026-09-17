from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path


class ArtifactStatus(StrEnum):
    """Lifecycle states for acquisition artifacts."""

    PLANNED = "PLANNED"
    DOWNLOADING = "DOWNLOADING"
    RECEIVED = "RECEIVED"
    HASHED = "HASHED"
    DECODED = "DECODED"
    VALIDATED = "VALIDATED"
    COMMITTED = "COMMITTED"
    NO_DATA = "NO_DATA"
    RETRYABLE = "RETRYABLE"
    FAILED_FATAL = "FAILED_FATAL"


@dataclass(frozen=True, slots=True)
class AcquisitionRequest:
    """Immutable acquisition request using a half-open UTC interval."""

    instrument: str
    start: datetime
    end: datetime


@dataclass(frozen=True, slots=True)
class DownloadChunk:
    """One deterministic Dukascopy hourly request."""

    instrument: str
    timestamp: datetime
    url: str


@dataclass(frozen=True, slots=True)
class ArtifactRecord:
    """Immutable metadata describing one raw artifact."""

    instrument: str
    timestamp: datetime
    path: Path
    byte_count: int
    sha256: str
    status: ArtifactStatus


@dataclass(frozen=True, slots=True)
class Tick:
    """Canonical decoded Dukascopy tick."""

    timestamp: datetime
    ask: float
    bid: float
    ask_volume: float
    bid_volume: float

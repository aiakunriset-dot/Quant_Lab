from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from .artifacts import atomic_write, sha256_file
from .contracts import ArtifactStatus, DownloadChunk
from .metadata import ManifestStore
from .planner import build_plan
from .transport import DukascopyTransport, NoDataError, TransportError, TransportConfig

LOGGER = logging.getLogger(__name__)


class AcquisitionService:
    """Resumable raw Dukascopy acquisition service."""

    VALIDATED_STATUS = ArtifactStatus.VALIDATED

    def __init__(self, root: Path, transport: DukascopyTransport | None = None) -> None:
        self.root = root
        self.manifest = ManifestStore(root / "manifests" / "acquisition.db")
        self.transport = transport or DukascopyTransport(TransportConfig())

    def plan(self, instrument: str, start: datetime, end: datetime) -> tuple[DownloadChunk, ...]:
        """Build the deterministic hourly plan."""
        return build_plan(instrument, start, end)

    def raw_path(self, chunk: DownloadChunk) -> Path:
        """Return the immutable raw artifact path for a chunk."""
        ts = chunk.timestamp
        return self.root / "raw" / "dukascopy" / chunk.instrument / f"{ts.year:04d}" / f"{ts.month - 1:02d}" / f"{ts.day:02d}" / f"{ts.hour:02d}h_ticks.bi5"

    @staticmethod
    def sha256(path: Path) -> str:
        """Return SHA-256 for a raw artifact."""
        return sha256_file(path)

    def is_verified(self, chunk: DownloadChunk) -> bool:
        """Return whether a manifest record and raw artifact hash agree."""
        row = self.manifest.get(chunk.instrument, chunk.timestamp)
        path = self.raw_path(chunk)
        if row is None or row["status"] != ArtifactStatus.VALIDATED.value or not path.is_file():
            return False
        return row["sha256"] == self.sha256(path)

    def download_chunk(self, chunk: DownloadChunk, overwrite: bool = False) -> ArtifactStatus:
        """Download one raw chunk with atomic commit and manifest update."""
        path = self.raw_path(chunk)
        if not overwrite and self.is_verified(chunk):
            return ArtifactStatus.VALIDATED
        self.manifest.upsert(chunk.instrument, chunk.timestamp, chunk.url, 0, None, ArtifactStatus.DOWNLOADING)
        try:
            response = self.transport.fetch(chunk.url)
        except NoDataError:
            self.manifest.upsert(chunk.instrument, chunk.timestamp, chunk.url, 0, None, ArtifactStatus.NO_DATA)
            return ArtifactStatus.NO_DATA
        except TransportError:
            self.manifest.upsert(chunk.instrument, chunk.timestamp, chunk.url, 0, None, ArtifactStatus.FAILED_FATAL)
            raise
        if not response.body:
            self.manifest.upsert(chunk.instrument, chunk.timestamp, chunk.url, 0, None, ArtifactStatus.FAILED_FATAL)
            raise TransportError(f"Empty successful response for {chunk.url}")
        atomic_write(path, response.body)
        digest = self.sha256(path)
        self.manifest.upsert(chunk.instrument, chunk.timestamp, chunk.url, len(response.body), digest, ArtifactStatus.HASHED)
        self.manifest.upsert(chunk.instrument, chunk.timestamp, chunk.url, len(response.body), digest, ArtifactStatus.VALIDATED)
        return ArtifactStatus.VALIDATED

    def download(self, chunks: tuple[DownloadChunk, ...], workers: int = 4, overwrite: bool = False) -> dict[ArtifactStatus, int]:
        """Download planned chunks concurrently and return status counts."""
        if workers < 1:
            raise ValueError("workers must be >= 1")
        counts = {status: 0 for status in ArtifactStatus}
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="dukascopy") as executor:
            futures = {executor.submit(self.download_chunk, chunk, overwrite): chunk for chunk in chunks}
            for future in as_completed(futures):
                status = future.result()
                counts[status] += 1
        return counts

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from .contracts import ArtifactStatus


class ManifestStore:
    """SQLite-backed acquisition manifest with idempotent upserts."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS artifacts (
                    instrument TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    url TEXT NOT NULL,
                    byte_count INTEGER NOT NULL,
                    sha256 TEXT,
                    status TEXT NOT NULL,
                    PRIMARY KEY (instrument, timestamp)
                )
                """
            )

    def upsert(
        self,
        instrument: str,
        timestamp: datetime,
        url: str,
        byte_count: int,
        sha256: str | None,
        status: ArtifactStatus,
    ) -> None:
        """Insert or update one acquisition record."""
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                INSERT INTO artifacts(instrument,timestamp,url,byte_count,sha256,status)
                VALUES(?,?,?,?,?,?)
                ON CONFLICT(instrument,timestamp) DO UPDATE SET
                    url=excluded.url,
                    byte_count=excluded.byte_count,
                    sha256=excluded.sha256,
                    status=excluded.status
                """,
                (instrument, timestamp.isoformat(), url, byte_count, sha256, status.value),
            )

    def get(self, instrument: str, timestamp: datetime) -> dict[str, Any] | None:
        """Return one manifest record or ``None``."""
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM artifacts WHERE instrument=? AND timestamp=?",
                (instrument, timestamp.isoformat()),
            ).fetchone()
        return dict(row) if row is not None else None

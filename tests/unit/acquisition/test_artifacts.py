from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from quantlab.acquisition.artifacts import atomic_write, sha256_file
from quantlab.acquisition.metadata import ManifestStore
from quantlab.acquisition.contracts import ArtifactStatus


def test_atomic_write_creates_exact_bytes(tmp_path: Path):
    target = tmp_path / "raw.bi5"
    atomic_write(target, b"abc")
    assert target.read_bytes() == b"abc"


def test_atomic_write_replaces_existing_atomically(tmp_path: Path):
    target = tmp_path / "raw.bi5"
    atomic_write(target, b"old")
    atomic_write(target, b"new")
    assert target.read_bytes() == b"new"


def test_sha256_file_matches_known_digest(tmp_path: Path):
    target = tmp_path / "raw.bi5"
    target.write_bytes(b"abc")
    assert sha256_file(target) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_sha256_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        sha256_file(tmp_path / "missing")


def test_manifest_round_trip(tmp_path: Path):
    db = ManifestStore(tmp_path / "manifest.db")
    timestamp = datetime(2024, 1, 1, tzinfo=timezone.utc)
    db.upsert("usa500idxusd", timestamp, "url", 3, "abc", ArtifactStatus.HASHED)
    row = db.get("usa500idxusd", timestamp)
    assert row is not None
    assert row["sha256"] == "abc"
    assert row["status"] == ArtifactStatus.HASHED.value

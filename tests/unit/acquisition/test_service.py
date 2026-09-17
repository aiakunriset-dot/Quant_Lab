from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from quantlab.acquisition.planner import build_plan
from quantlab.acquisition.service import AcquisitionService


def test_plan_only_returns_deterministic_chunks(tmp_path: Path):
    service = AcquisitionService(tmp_path)
    chunks = service.plan("usa500idxusd", datetime(2024, 1, 1, tzinfo=timezone.utc), datetime(2024, 1, 1, 2, tzinfo=timezone.utc))
    assert len(chunks) == 2
    assert chunks[0].url.endswith("/2024/00/01/00h_ticks.bi5")


def test_raw_path_is_stable(tmp_path: Path):
    service = AcquisitionService(tmp_path)
    chunk = build_plan("usa500idxusd", datetime(2024, 1, 1, tzinfo=timezone.utc), datetime(2024, 1, 1, 1, tzinfo=timezone.utc))[0]
    assert service.raw_path(chunk) == tmp_path / "raw" / "dukascopy" / "usa500idxusd" / "2024" / "00" / "01" / "00h_ticks.bi5"


def test_existing_verified_artifact_is_skipped(tmp_path: Path):
    service = AcquisitionService(tmp_path)
    chunk = build_plan("usa500idxusd", datetime(2024, 1, 1, tzinfo=timezone.utc), datetime(2024, 1, 1, 1, tzinfo=timezone.utc))[0]
    path = service.raw_path(chunk)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"abc")
    service.manifest.upsert("usa500idxusd", chunk.timestamp, chunk.url, 3, service.sha256(path), service.VALIDATED_STATUS)
    assert service.is_verified(chunk)


def test_missing_artifact_is_not_verified(tmp_path: Path):
    service = AcquisitionService(tmp_path)
    chunk = build_plan("usa500idxusd", datetime(2024, 1, 1, tzinfo=timezone.utc), datetime(2024, 1, 1, 1, tzinfo=timezone.utc))[0]
    assert not service.is_verified(chunk)


def test_sha256_is_stable(tmp_path: Path):
    service = AcquisitionService(tmp_path)
    path = tmp_path / "x"
    path.write_bytes(b"abc")
    assert service.sha256(path) == service.sha256(path)

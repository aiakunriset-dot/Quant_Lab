from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json


def build_colab_manifest(
    task_id: str,
    git_revision: str,
    datasets: list[str],
    config_sha256: str,
    seed: int,
) -> dict[str, object]:
    """Build a deterministic Colab reproducibility manifest."""
    if len(config_sha256) != 64:
        raise ValueError("config_sha256 must be a SHA-256 digest")
    payload: dict[str, object] = {
        "schema_version": "1",
        "task_id": task_id,
        "git_revision": git_revision,
        "datasets": sorted(datasets),
        "config_sha256": config_sha256,
        "seed": seed,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    stable = json.dumps({k: v for k, v in payload.items() if k != "created_at"}, sort_keys=True, separators=(",", ":"))
    payload["manifest_sha256"] = hashlib.sha256(stable.encode("utf-8")).hexdigest()
    return payload

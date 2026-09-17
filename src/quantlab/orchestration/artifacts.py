from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Compute a streaming SHA-256 digest for a file."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()

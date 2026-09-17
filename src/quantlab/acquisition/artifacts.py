from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Return SHA-256 for a file without loading it fully into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, payload: bytes) -> None:
    """Atomically write bytes and replace any existing destination."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

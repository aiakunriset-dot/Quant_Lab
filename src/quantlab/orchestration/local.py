from __future__ import annotations

from pathlib import Path


def build_aider_command(model: str, files: list[str]) -> list[str]:
    """Build a safe argument-vector for an Aider implementation run."""
    if not model.strip():
        raise ValueError("model is required")
    if not files:
        raise ValueError("at least one file is required")
    return ["aider", "--model", model, "--no-auto-commits", "--no-gitignore", *files]


def validate_project_root(root: Path, expected_name: str = "QUANT_LAB") -> Path:
    """Validate and return an existing Quant_Lab root directory."""
    resolved = Path(root).resolve()
    if resolved.name.lower() != expected_name.lower():
        raise ValueError(f"project root must end with {expected_name}: {resolved}")
    if not resolved.is_dir():
        raise FileNotFoundError(resolved)
    return resolved

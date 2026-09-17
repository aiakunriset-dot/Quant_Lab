from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

_ALLOWED_SECRETS = (
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GITHUB_TOKEN",
    "GOOGLE_APPLICATION_CREDENTIALS",
)


@dataclass(frozen=True, slots=True)
class ControlPlaneConfig:
    """Non-secret control-plane configuration."""

    project_root: Path
    gdrive_root: str = "Quant_Lab"
    github_repo: str = "aiakunriset-dot/Quant_Lab"
    require_clean_git: bool = True

    @classmethod
    def from_environment(cls, project_root: str | Path) -> "ControlPlaneConfig":
        """Build configuration from safe environment values only."""
        root = Path(project_root).expanduser()
        gdrive_root = os.getenv("QUANTLAB_GDRIVE_ROOT", "Quant_Lab").strip() or "Quant_Lab"
        github_repo = os.getenv("QUANTLAB_GITHUB_REPO", "aiakunriset-dot/Quant_Lab").strip()
        return cls(project_root=root, gdrive_root=gdrive_root, github_repo=github_repo)

    def secret_status(self) -> dict[str, bool]:
        """Return only boolean presence flags for approved secret variables."""
        return {name: bool(os.getenv(name)) for name in _ALLOWED_SECRETS}

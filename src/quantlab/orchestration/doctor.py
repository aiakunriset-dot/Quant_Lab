from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import shutil
import subprocess

from quantlab.orchestration.config import ControlPlaneConfig


@dataclass(frozen=True, slots=True)
class CheckResult:
    """One non-secret environment diagnostic result."""

    name: str
    status: str
    detail: str


def check_project_root(value: str | Path) -> bool:
    """Check whether a path has the locked Quant_Lab root name."""
    return Path(value).name.lower() == "quant_lab"


def _command_version(command: str) -> str | None:
    """Return a tool version without raising on missing executables."""
    executable = shutil.which(command)
    if executable is None:
        return None
    try:
        completed = subprocess.run(
            [executable, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    output = (completed.stdout or completed.stderr).strip().splitlines()
    return output[0] if output else "installed"


def run_doctor(config: ControlPlaneConfig) -> list[CheckResult]:
    """Run local control-plane diagnostics without network calls or secret leakage."""
    checks: list[CheckResult] = []
    checks.append(
        CheckResult(
            "project_root",
            "PASS" if check_project_root(config.project_root) and config.project_root.is_dir() else "FAIL",
            str(config.project_root),
        )
    )
    for command in ("python", "git", "aider"):
        version = _command_version(command)
        checks.append(CheckResult(command, "PASS" if version else "MISSING", version or "not found"))
    secret_status = config.secret_status()
    for name, configured in secret_status.items():
        checks.append(CheckResult(f"credential:{name}", "CONFIGURED" if configured else "MISSING", "presence only"))
    return checks


def doctor_dict(config: ControlPlaneConfig) -> list[dict[str, str]]:
    """Return diagnostics as JSON-safe dictionaries."""
    return [asdict(result) for result in run_doctor(config)]

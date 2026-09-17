from dataclasses import dataclass


@dataclass(frozen=True)
class GateResult:
    """Machine-readable validation result."""

    name: str
    passed: bool
    message: str


def require_passed(result: GateResult) -> None:
    """Raise when a validation gate fails."""
    if not result.passed:
        raise ValueError(f"Validation gate failed: {result.name}: {result.message}")

from dataclasses import dataclass


@dataclass(frozen=True)
class StatisticalGate:
    """Configuration contract for research promotion gates."""

    min_observations: int
    require_out_of_sample: bool
    require_walk_forward: bool
    require_cost_model: bool

    def validate(self) -> None:
        """Validate statistical-gate configuration."""
        if self.min_observations <= 0:
            raise ValueError("min_observations must be positive")

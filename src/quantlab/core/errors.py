class QuantLabError(Exception):
    """Base exception for Quant_Lab."""


class ConfigurationError(QuantLabError):
    """Raised when configuration is invalid."""


class DataIntegrityError(QuantLabError):
    """Raised when market-data integrity constraints are violated."""


class ValidationError(QuantLabError):
    """Raised when a validation gate fails."""

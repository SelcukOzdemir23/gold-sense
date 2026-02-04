class GoldSenseError(Exception):
    """Base error for the Gold-Sense AI system."""


class ConfigError(GoldSenseError):
    """Raised when configuration is missing or invalid."""


class ExternalServiceError(GoldSenseError):
    """Raised when an external service call fails."""

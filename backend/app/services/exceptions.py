"""Custom exceptions for Earth Engine services."""


class EarthEngineError(Exception):
    """Base exception for Earth Engine errors."""

    pass


class EarthEngineQuotaError(EarthEngineError):
    """Raised when GEE quota is exceeded."""

    pass


class EarthEngineAuthError(EarthEngineError):
    """Raised when GEE authentication fails."""

    pass


class InvalidGeometryError(EarthEngineError):
    """Raised when farm geometry is invalid."""

    pass


class InvalidDateRangeError(EarthEngineError):
    """Raised when date range is invalid."""

    pass


class SatelliteHealthCheckError(Exception):
    """Raised when satellite health check fails."""

    pass

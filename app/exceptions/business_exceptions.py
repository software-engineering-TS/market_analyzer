"""Business-level exceptions."""


class BusinessException(Exception):
    """Base class for business exceptions."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ResourceNotFoundException(BusinessException):
    """Raised when a requested resource does not exist."""


class MarketDataUnavailableException(BusinessException):
    """Raised when an external market-data provider cannot return data."""

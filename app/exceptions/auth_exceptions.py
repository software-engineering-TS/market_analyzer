"""Custom authentication exceptions."""


class AuthenticationError(Exception):
    """Raised when authentication fails."""


class UserAlreadyExistsError(Exception):
    """Raised when attempting to register an existing user."""


class TokenStoreUnavailableError(Exception):
    """Raised when production token-revocation storage is unavailable."""

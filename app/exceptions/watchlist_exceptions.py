"""Watchlist domain exceptions."""


class WatchlistNotFoundError(Exception):
    """Raised when a requested watchlist item does not exist."""


class WatchlistAlreadyExistsError(Exception):
    """Raised when the user already follows the requested symbol."""

"""Watchlist domain errors."""
from app.core.errors import AppError


class WatchlistError(AppError):
    """Base error for watchlist domain."""
    pass


class WatchlistItemNotFoundError(WatchlistError):
    """Raised when watchlist item is not found."""

    def __init__(self, item_id: int = None, symbol: str = None):
        if symbol:
            message = f"Symbol '{symbol}' not found in watchlist"
        else:
            message = f"Watchlist item with ID {item_id} not found"
        super().__init__(message, status_code=404, error_code="WATCHLIST_ITEM_NOT_FOUND")


class WatchlistItemAlreadyExistsError(WatchlistError):
    """Raised when trying to add a symbol that already exists in watchlist."""

    def __init__(self, symbol: str):
        super().__init__(
            f"Symbol '{symbol}' already exists in your watchlist",
            status_code=409,
            error_code="WATCHLIST_ITEM_EXISTS",
        )


class WatchlistLimitExceededError(WatchlistError):
    """Raised when user exceeds maximum watchlist items."""

    def __init__(self, max_items: int = 50):
        super().__init__(
            f"Watchlist limit exceeded. Maximum {max_items} items allowed",
            status_code=400,
            error_code="WATCHLIST_LIMIT_EXCEEDED",
        )

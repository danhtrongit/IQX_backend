"""Repository protocols (interfaces) for watchlist domain."""
from typing import Protocol, Optional
from app.domain.watchlist.entities import WatchlistItem


class WatchlistRepository(Protocol):
    """Watchlist repository interface."""

    async def get_by_id(self, item_id: int) -> Optional[WatchlistItem]:
        """Get watchlist item by ID."""
        ...

    async def get_by_user_and_symbol(
        self, user_id: int, symbol: str
    ) -> Optional[WatchlistItem]:
        """Get watchlist item by user ID and symbol."""
        ...

    async def get_all_by_user(
        self, user_id: int, limit: int = 100, offset: int = 0
    ) -> list[WatchlistItem]:
        """Get all watchlist items for a user."""
        ...

    async def count_by_user(self, user_id: int) -> int:
        """Count total watchlist items for a user."""
        ...

    async def create(
        self,
        user_id: int,
        symbol: str,
        notes: Optional[str] = None,
        target_price: Optional[float] = None,
        alert_enabled: bool = False,
    ) -> WatchlistItem:
        """Create a new watchlist item."""
        ...

    async def update(
        self,
        item_id: int,
        notes: Optional[str] = None,
        target_price: Optional[float] = None,
        alert_enabled: Optional[bool] = None,
        position: Optional[int] = None,
    ) -> Optional[WatchlistItem]:
        """Update a watchlist item."""
        ...

    async def delete(self, item_id: int) -> bool:
        """Delete a watchlist item."""
        ...

    async def delete_by_user_and_symbol(self, user_id: int, symbol: str) -> bool:
        """Delete a watchlist item by user ID and symbol."""
        ...

    async def exists(self, user_id: int, symbol: str) -> bool:
        """Check if a symbol exists in user's watchlist."""
        ...

    async def bulk_create(
        self, user_id: int, symbols: list[str]
    ) -> list[WatchlistItem]:
        """Bulk create watchlist items."""
        ...

    async def reorder(
        self, user_id: int, item_positions: list[tuple[int, int]]
    ) -> None:
        """Reorder watchlist items. item_positions is list of (item_id, position)."""
        ...

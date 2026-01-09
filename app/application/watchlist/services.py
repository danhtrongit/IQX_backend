"""Watchlist application service."""
from app.domain.watchlist.entities import WatchlistItem
from app.domain.watchlist.errors import (
    WatchlistItemNotFoundError,
    WatchlistItemAlreadyExistsError,
    WatchlistLimitExceededError,
)
from app.domain.watchlist.repositories import WatchlistRepository
from app.application.watchlist.dtos import (
    AddWatchlistItemRequest,
    UpdateWatchlistItemRequest,
    BulkAddWatchlistRequest,
    ReorderWatchlistRequest,
    WatchlistItemResponse,
    WatchlistResponse,
)

MAX_WATCHLIST_ITEMS = 50


class WatchlistService:
    """Watchlist service - orchestrates watchlist use cases."""

    def __init__(self, watchlist_repo: WatchlistRepository):
        self.watchlist_repo = watchlist_repo

    async def get_watchlist(
        self,
        user_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> WatchlistResponse:
        """Get user's watchlist."""
        items = await self.watchlist_repo.get_all_by_user(user_id, limit, offset)
        total = await self.watchlist_repo.count_by_user(user_id)

        return WatchlistResponse(
            items=[self._to_response(item) for item in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_item(self, user_id: int, item_id: int) -> WatchlistItemResponse:
        """Get single watchlist item."""
        item = await self.watchlist_repo.get_by_id(item_id)

        if not item or item.user_id != user_id:
            raise WatchlistItemNotFoundError(item_id=item_id)

        return self._to_response(item)

    async def add_item(
        self,
        user_id: int,
        request: AddWatchlistItemRequest,
    ) -> WatchlistItemResponse:
        """Add symbol to user's watchlist."""
        # Check limit
        count = await self.watchlist_repo.count_by_user(user_id)
        if count >= MAX_WATCHLIST_ITEMS:
            raise WatchlistLimitExceededError(MAX_WATCHLIST_ITEMS)

        # Check duplicate
        if await self.watchlist_repo.exists(user_id, request.symbol):
            raise WatchlistItemAlreadyExistsError(request.symbol)

        # Create item
        item = await self.watchlist_repo.create(
            user_id=user_id,
            symbol=request.symbol,
            notes=request.notes,
            target_price=request.target_price,
            alert_enabled=request.alert_enabled,
        )

        return self._to_response(item)

    async def update_item(
        self,
        user_id: int,
        item_id: int,
        request: UpdateWatchlistItemRequest,
    ) -> WatchlistItemResponse:
        """Update watchlist item."""
        # Verify ownership
        existing = await self.watchlist_repo.get_by_id(item_id)
        if not existing or existing.user_id != user_id:
            raise WatchlistItemNotFoundError(item_id=item_id)

        # Update
        item = await self.watchlist_repo.update(
            item_id=item_id,
            notes=request.notes,
            target_price=request.target_price,
            alert_enabled=request.alert_enabled,
        )

        return self._to_response(item)

    async def remove_item(self, user_id: int, item_id: int) -> bool:
        """Remove item from watchlist."""
        # Verify ownership
        existing = await self.watchlist_repo.get_by_id(item_id)
        if not existing or existing.user_id != user_id:
            raise WatchlistItemNotFoundError(item_id=item_id)

        return await self.watchlist_repo.delete(item_id)

    async def remove_by_symbol(self, user_id: int, symbol: str) -> bool:
        """Remove item by symbol."""
        if not await self.watchlist_repo.exists(user_id, symbol):
            raise WatchlistItemNotFoundError(symbol=symbol)

        return await self.watchlist_repo.delete_by_user_and_symbol(user_id, symbol)

    async def bulk_add(
        self,
        user_id: int,
        request: BulkAddWatchlistRequest,
    ) -> list[WatchlistItemResponse]:
        """Bulk add symbols to watchlist."""
        # Check limit
        count = await self.watchlist_repo.count_by_user(user_id)
        if count + len(request.symbols) > MAX_WATCHLIST_ITEMS:
            raise WatchlistLimitExceededError(MAX_WATCHLIST_ITEMS)

        items = await self.watchlist_repo.bulk_create(user_id, request.symbols)
        return [self._to_response(item) for item in items]

    async def reorder(
        self,
        user_id: int,
        request: ReorderWatchlistRequest,
    ) -> None:
        """Reorder watchlist items."""
        item_positions = [(item["id"], item["position"]) for item in request.items]
        await self.watchlist_repo.reorder(user_id, item_positions)

    async def check_symbol_in_watchlist(self, user_id: int, symbol: str) -> bool:
        """Check if symbol is in user's watchlist."""
        return await self.watchlist_repo.exists(user_id, symbol)

    @staticmethod
    def _to_response(item: WatchlistItem) -> WatchlistItemResponse:
        """Convert entity to response DTO."""
        return WatchlistItemResponse(
            id=item.id,
            symbol=item.symbol,
            notes=item.notes,
            target_price=item.target_price,
            alert_enabled=item.alert_enabled,
            position=item.position,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

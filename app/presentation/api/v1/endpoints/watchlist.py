"""Watchlist API endpoints."""
from fastapi import APIRouter, Query

from app.application.watchlist.dtos import (
    AddWatchlistItemRequest,
    UpdateWatchlistItemRequest,
    BulkAddWatchlistRequest,
    ReorderWatchlistRequest,
    WatchlistItemResponse,
    WatchlistResponse,
)
from app.application.watchlist.services import WatchlistService
from app.infrastructure.repositories.watchlist_repo import SQLAlchemyWatchlistRepository
from app.presentation.deps.auth_deps import CurrentUser, DBSession

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


def get_watchlist_service(db: DBSession) -> WatchlistService:
    """Create watchlist service with dependencies."""
    return WatchlistService(
        watchlist_repo=SQLAlchemyWatchlistRepository(db),
    )


@router.get("", response_model=WatchlistResponse)
async def get_watchlist(
    db: DBSession,
    current_user: CurrentUser,
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> WatchlistResponse:
    """Get user's watchlist with pagination."""
    service = get_watchlist_service(db)
    return await service.get_watchlist(current_user.id, limit, offset)


@router.get("/{item_id}", response_model=WatchlistItemResponse)
async def get_watchlist_item(
    item_id: int,
    db: DBSession,
    current_user: CurrentUser,
) -> WatchlistItemResponse:
    """Get a single watchlist item."""
    service = get_watchlist_service(db)
    return await service.get_item(current_user.id, item_id)


@router.post("", response_model=WatchlistItemResponse, status_code=201)
async def add_to_watchlist(
    request: AddWatchlistItemRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> WatchlistItemResponse:
    """Add a symbol to watchlist."""
    service = get_watchlist_service(db)
    return await service.add_item(current_user.id, request)


@router.post("/bulk", response_model=list[WatchlistItemResponse], status_code=201)
async def bulk_add_to_watchlist(
    request: BulkAddWatchlistRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> list[WatchlistItemResponse]:
    """Bulk add symbols to watchlist."""
    service = get_watchlist_service(db)
    return await service.bulk_add(current_user.id, request)


@router.put("/{item_id}", response_model=WatchlistItemResponse)
async def update_watchlist_item(
    item_id: int,
    request: UpdateWatchlistItemRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> WatchlistItemResponse:
    """Update a watchlist item."""
    service = get_watchlist_service(db)
    return await service.update_item(current_user.id, item_id, request)


@router.delete("/{item_id}", status_code=204)
async def remove_from_watchlist(
    item_id: int,
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    """Remove an item from watchlist by ID."""
    service = get_watchlist_service(db)
    await service.remove_item(current_user.id, item_id)


@router.delete("/symbol/{symbol}", status_code=204)
async def remove_symbol_from_watchlist(
    symbol: str,
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    """Remove a symbol from watchlist."""
    service = get_watchlist_service(db)
    await service.remove_by_symbol(current_user.id, symbol)


@router.post("/reorder", status_code=204)
async def reorder_watchlist(
    request: ReorderWatchlistRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    """Reorder watchlist items."""
    service = get_watchlist_service(db)
    await service.reorder(current_user.id, request)


@router.get("/check/{symbol}", response_model=dict)
async def check_symbol_in_watchlist(
    symbol: str,
    db: DBSession,
    current_user: CurrentUser,
) -> dict:
    """Check if a symbol is in user's watchlist."""
    service = get_watchlist_service(db)
    exists = await service.check_symbol_in_watchlist(current_user.id, symbol)
    return {"symbol": symbol.upper(), "in_watchlist": exists}

"""Watchlist DTOs (Data Transfer Objects)."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# === Request DTOs ===

class AddWatchlistItemRequest(BaseModel):
    """Add symbol to watchlist request."""

    symbol: str = Field(..., min_length=1, max_length=20, description="Stock symbol (e.g., VCB, VNM)")
    notes: Optional[str] = Field(None, max_length=500, description="Personal notes")
    target_price: Optional[float] = Field(None, gt=0, description="Target price for alerts")
    alert_enabled: bool = Field(False, description="Enable price alerts")


class UpdateWatchlistItemRequest(BaseModel):
    """Update watchlist item request."""

    notes: Optional[str] = Field(None, max_length=500)
    target_price: Optional[float] = Field(None, gt=0)
    alert_enabled: Optional[bool] = None


class BulkAddWatchlistRequest(BaseModel):
    """Bulk add symbols to watchlist."""

    symbols: list[str] = Field(..., min_length=1, max_length=20, description="List of stock symbols")


class ReorderWatchlistRequest(BaseModel):
    """Reorder watchlist items."""

    items: list[dict] = Field(
        ...,
        min_length=1,
        description="List of {id: int, position: int}",
    )


# === Response DTOs ===

class WatchlistItemResponse(BaseModel):
    """Single watchlist item response."""

    id: int
    symbol: str
    notes: Optional[str] = None
    target_price: Optional[float] = None
    alert_enabled: bool
    position: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WatchlistResponse(BaseModel):
    """Paginated watchlist response."""

    items: list[WatchlistItemResponse]
    total: int
    limit: int
    offset: int

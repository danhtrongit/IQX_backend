"""Watchlist domain entities."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class WatchlistItem:
    """Watchlist item entity - represents a stock symbol that user is tracking."""

    id: int
    user_id: int
    symbol: str
    notes: Optional[str] = None
    target_price: Optional[float] = None
    alert_enabled: bool = False
    position: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

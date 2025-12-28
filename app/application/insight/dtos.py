
"""Insight/Analysis DTOs."""

from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field


# === Top Foreign DTOs ===


class TopForeignItem(BaseModel):
    """Top foreign buy/sell item."""

    symbol: str
    date: Optional[str] = None
    net_value: Optional[float] = None


class TopForeignResponse(BaseModel):
    """Top foreign response."""

    type: str  # buy or sell
    date: Optional[str] = None
    data: List[TopForeignItem]
    count: int


# === Top Stock DTOs ===


class TopStockItem(BaseModel):
    """Top stock item (gainer, loser, value, volume)."""

    symbol: str
    last_price: Optional[float] = None
    price_change: Optional[float] = Field(None, alias="price_change_1d")
    price_change_pct: Optional[float] = Field(None, alias="price_change_pct_1d")
    accumulated_value: Optional[float] = None
    avg_volume_20d: Optional[float] = None
    volume_spike_pct: Optional[float] = Field(None, alias="volume_spike_20d_pct")

    class Config:
        populate_by_name = True


class TopStockResponse(BaseModel):
    """Top stock response."""

    type: str  # gainer, loser, value, volume, deal
    index: str
    data: List[Dict[str, Any]]
    count: int


# === Proprietary Trading DTOs ===


class ProprietaryTradingItem(BaseModel):
    """Proprietary trading item."""

    trading_date: Optional[str] = None
    buy_volume: Optional[float] = None
    buy_value: Optional[float] = None
    sell_volume: Optional[float] = None
    sell_value: Optional[float] = None
    net_volume: Optional[float] = None
    net_value: Optional[float] = None
    total_volume: Optional[float] = None
    total_value: Optional[float] = None


class ProprietaryTradingResponse(BaseModel):
    """Proprietary trading response."""

    symbol: str
    data: List[ProprietaryTradingItem]
    count: int


# === Foreign Trading DTOs ===


class ForeignTradingItem(BaseModel):
    """Foreign trading item per symbol."""

    trading_date: Optional[str] = None
    buy_volume: Optional[float] = None
    buy_value: Optional[float] = None
    sell_volume: Optional[float] = None
    sell_value: Optional[float] = None
    net_volume: Optional[float] = None
    net_value: Optional[float] = None
    total_room: Optional[float] = None
    current_room: Optional[float] = None
    owned_percent: Optional[float] = None


class ForeignTradingResponse(BaseModel):
    """Foreign trading response per symbol."""

    symbol: str
    data: List[ForeignTradingItem]
    count: int

# === Order/Side Stats DTOs ===

class OrderStatsResponse(BaseModel):
    symbol: str
    data: List[Dict[str, Any]]
    count: int

class SideStatsResponse(BaseModel):
    symbol: str
    data: List[Dict[str, Any]]
    count: int


# === Insider Trading DTOs ===


class InsiderTradingItem(BaseModel):
    """Insider trading item (giao dich noi bo)."""

    start_date: Optional[str] = None
    end_date: Optional[str] = None
    public_date: Optional[str] = None
    share_before_trade: Optional[float] = None
    share_after_trade: Optional[float] = None
    share_register: Optional[float] = None
    share_acquire: Optional[float] = None
    ownership_after_trade: Optional[float] = None
    trader_organ_name: Optional[str] = None
    action_type: Optional[str] = None
    trade_status: Optional[str] = None


class InsiderTradingResponse(BaseModel):
    """Insider trading response."""

    symbol: str
    data: List[InsiderTradingItem]
    count: int

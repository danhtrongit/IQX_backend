"""Quote DTOs."""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Any
from pydantic import BaseModel, Field


# === Request DTOs ===

class HistoryRequest(BaseModel):
    """Historical price request."""
    
    start: str = Field(..., description="Start date (YYYY-MM-DD)")
    end: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    interval: str = Field("1D", description="Interval: 1m, 5m, 15m, 30m, 1H, 1D, 1W, 1M")
    count_back: Optional[int] = Field(None, ge=1, le=5000, description="Number of candles")


class IntradayRequest(BaseModel):
    """Intraday trades request."""
    
    page_size: int = Field(100, ge=1, le=5000, description="Number of trades")
    last_time: Optional[str] = Field(None, description="Get trades after this time")


class PriceBoardRequest(BaseModel):
    """Price board request."""
    
    symbols: List[str] = Field(..., min_length=1, max_length=1000, description="List of symbols (max 1000)")


class TradingStatsRequest(BaseModel):
    """Trading statistics request."""
    
    resolution: str = Field("1D", description="Resolution: 1D, 1W, 1M")
    start: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    limit: int = Field(100, ge=1, le=1000)


# === Response DTOs ===

class OHLCVItem(BaseModel):
    """OHLCV candle item."""
    
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class HistoryResponse(BaseModel):
    """Historical price response."""
    
    symbol: str
    interval: str
    data: List[OHLCVItem]
    count: int


class IntradayItem(BaseModel):
    """Intraday trade item."""
    
    time: datetime
    price: float
    volume: int
    side: Optional[str] = None  # BUY, SELL, UNKNOWN


class IntradayResponse(BaseModel):
    """Intraday trades response."""
    
    symbol: str
    data: List[IntradayItem]
    count: int


class PriceInfo(BaseModel):
    """Current price info for a symbol."""
    
    symbol: str
    exchange: Optional[str] = None
    organ_name: Optional[str] = None
    
    # Match price
    price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    value: Optional[float] = None
    
    # Reference prices
    ref_price: Optional[float] = None
    ceiling: Optional[float] = None
    floor: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    
    # Bid/Ask
    bid_1_price: Optional[float] = None
    bid_1_volume: Optional[int] = None
    bid_2_price: Optional[float] = None
    bid_2_volume: Optional[int] = None
    bid_3_price: Optional[float] = None
    bid_3_volume: Optional[int] = None
    ask_1_price: Optional[float] = None
    ask_1_volume: Optional[int] = None
    ask_2_price: Optional[float] = None
    ask_2_volume: Optional[int] = None
    ask_3_price: Optional[float] = None
    ask_3_volume: Optional[int] = None
    
    # Foreign
    foreign_buy_volume: Optional[int] = None
    foreign_sell_volume: Optional[int] = None


class PriceBoardResponse(BaseModel):
    """Price board response."""
    
    data: List[PriceInfo]
    count: int


class PriceDepthItem(BaseModel):
    """Price depth item."""
    
    price: float
    volume: int
    buy_volume: Optional[int] = None
    sell_volume: Optional[int] = None


class PriceDepthResponse(BaseModel):
    """Price depth response."""
    
    symbol: str
    data: List[PriceDepthItem]


class TradingStatsItem(BaseModel):
    """Trading statistics item."""
    
    trading_date: datetime
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    matched_volume: Optional[int] = None
    matched_value: Optional[float] = None
    deal_volume: Optional[int] = None
    deal_value: Optional[float] = None


class TradingStatsResponse(BaseModel):
    """Trading statistics response."""
    
    symbol: str
    data: List[TradingStatsItem]
    count: int

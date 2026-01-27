"""DTOs for AI Insight API."""
from typing import Optional, List
from pydantic import BaseModel, Field


class OHLCDataPoint(BaseModel):
    """Single OHLC data point with MA values."""
    trade_date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    ma10: Optional[float] = None
    ma20: Optional[float] = None
    ma30: Optional[float] = None
    ma100: Optional[float] = None
    ma200: Optional[float] = None
    vol_ma10: Optional[int] = None
    vol_ma20: Optional[int] = None
    vol_ma30: Optional[int] = None
    vol_ma100: Optional[int] = None
    vol_ma200: Optional[int] = None


class AIInsightRequest(BaseModel):
    """Request for AI Insight analysis."""
    period: int = Field(
        default=20,
        description="Number of days for analysis: 10, 20, 30, 100, or 200"
    )


class TradingRecommendation(BaseModel):
    """Trading recommendation from AI analysis."""
    description: str = Field(description="Mô tả phân tích kỹ thuật")
    buy_price: Optional[str] = Field(None, description="Giá mua đề xuất")
    buy_conditions: List[str] = Field(default_factory=list, description="Điều kiện mua")
    stop_loss_price: Optional[str] = Field(None, description="Giá cắt lỗ")
    stop_loss_conditions: List[str] = Field(default_factory=list, description="Điều kiện cắt lỗ")
    take_profit_price: Optional[str] = Field(None, description="Giá chốt lời")
    take_profit_conditions: List[str] = Field(default_factory=list, description="Điều kiện chốt lời")


class AIInsightResponse(BaseModel):
    """Response from AI Insight analysis."""
    symbol: str
    period: int
    current_price: Optional[float] = None
    current_volume: Optional[int] = None
    recommendation: Optional[TradingRecommendation] = None
    raw_analysis: Optional[str] = None
    candlestick_pattern: Optional[str] = None
    error: Optional[str] = None

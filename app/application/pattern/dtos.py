"""DTOs for pattern module."""
from pydantic import BaseModel
from typing import Optional


class CandlestickPatternDTO(BaseModel):
    """DTO for candlestick pattern."""
    id: int
    name: str
    style: str
    signal: str
    reliability: str
    description: str
    image: str


class ChartPatternDTO(BaseModel):
    """DTO for chart pattern."""
    id: int
    name: str
    style: str
    description: str
    strategy: str
    image: str


class StockCandlestickPatternDTO(BaseModel):
    """DTO for stock candlestick pattern detection."""
    symbol: str
    patterns: list[str]


class StockChartPatternDTO(BaseModel):
    """DTO for stock chart pattern detection."""
    symbol: str
    model: str


class CandlestickPatternListResponse(BaseModel):
    """Response for listing all candlestick patterns."""
    patterns: list[CandlestickPatternDTO]
    metadata: dict


class ChartPatternListResponse(BaseModel):
    """Response for listing all chart patterns."""
    patterns: list[ChartPatternDTO]
    metadata: dict


class StockPatternsResponse(BaseModel):
    """Response containing stock patterns."""
    candlestick_patterns: list[StockCandlestickPatternDTO]
    chart_patterns: list[StockChartPatternDTO]


class PatternBySymbolResponse(BaseModel):
    """Response for patterns by symbol."""
    symbol: str
    candlestick_patterns: list[CandlestickPatternDTO]
    chart_pattern: Optional[ChartPatternDTO] = None

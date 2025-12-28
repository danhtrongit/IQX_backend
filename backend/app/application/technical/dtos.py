"""Technical Analysis DTOs for Vietcap IQ API."""

from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from enum import Enum


class TechnicalRating(str, Enum):
    """Technical indicator rating."""
    VERY_GOOD = "VERY_GOOD"
    GOOD = "GOOD"
    NEUTRAL = "NEUTRAL"
    BAD = "BAD"
    VERY_BAD = "VERY_BAD"


class TechnicalTimeframe(str, Enum):
    """Technical analysis timeframe."""
    ONE_HOUR = "ONE_HOUR"
    ONE_DAY = "ONE_DAY"
    ONE_WEEK = "ONE_WEEK"


class GaugeValues(BaseModel):
    """Gauge values for BUY/NEUTRAL/SELL counts."""
    buy: int = Field(0, alias="BUY")
    neutral: int = Field(0, alias="NEUTRAL")
    sell: int = Field(0, alias="SELL")

    class Config:
        populate_by_name = True


class GaugeData(BaseModel):
    """Gauge data with rating and values."""
    rating: Optional[str] = None
    values: Optional[GaugeValues] = None


class IndicatorItem(BaseModel):
    """Individual indicator (MA or Oscillator)."""
    name: str
    rating: Optional[str] = None
    value: Optional[float] = None


class PivotData(BaseModel):
    """Pivot point and support/resistance levels."""
    pivot_point: Optional[float] = Field(None, alias="pivotPoint")
    # Classic Pivot
    resistance1: Optional[float] = None
    resistance2: Optional[float] = None
    resistance3: Optional[float] = None
    support1: Optional[float] = None
    support2: Optional[float] = None
    support3: Optional[float] = None
    # Fibonacci
    fib_resistance1: Optional[float] = Field(None, alias="fibResistance1")
    fib_resistance2: Optional[float] = Field(None, alias="fibResistance2")
    fib_resistance3: Optional[float] = Field(None, alias="fibResistance3")
    fib_support1: Optional[float] = Field(None, alias="fibSupport1")
    fib_support2: Optional[float] = Field(None, alias="fibSupport2")
    fib_support3: Optional[float] = Field(None, alias="fibSupport3")
    # Camarilla
    camarilla_resistance1: Optional[float] = Field(None, alias="camarillaResistance1")
    camarilla_resistance2: Optional[float] = Field(None, alias="camarillaResistance2")
    camarilla_resistance3: Optional[float] = Field(None, alias="camarillaResistance3")
    camarilla_support1: Optional[float] = Field(None, alias="camarillaSupport1")
    camarilla_support2: Optional[float] = Field(None, alias="camarillaSupport2")
    camarilla_support3: Optional[float] = Field(None, alias="camarillaSupport3")
    # Woodie
    woodie_resistance1: Optional[float] = Field(None, alias="woodieResistance1")
    woodie_resistance2: Optional[float] = Field(None, alias="woodieResistance2")
    woodie_support1: Optional[float] = Field(None, alias="woodieSupport1")
    woodie_support2: Optional[float] = Field(None, alias="woodieSupport2")
    woodie_pivot: Optional[float] = Field(None, alias="woodiePivot")
    # DeMark
    demark_high: Optional[float] = Field(None, alias="demarkHigh")
    demark_low: Optional[float] = Field(None, alias="demarkLow")
    demark_pivot: Optional[float] = Field(None, alias="demarkPivot")

    class Config:
        populate_by_name = True


class TechnicalAnalysisData(BaseModel):
    """Complete technical analysis data."""
    symbol: str
    timeframe: str
    price: Optional[float] = None
    match_time: Optional[str] = Field(None, alias="matchTime")
    
    # Gauge summaries
    gauge_summary: Optional[GaugeData] = Field(None, alias="gaugeSummary")
    gauge_moving_average: Optional[GaugeData] = Field(None, alias="gaugeMovingAverage")
    gauge_oscillator: Optional[GaugeData] = Field(None, alias="gaugeOscillator")
    
    # Indicators
    moving_averages: Optional[List[IndicatorItem]] = Field(None, alias="movingAverages")
    oscillators: Optional[List[IndicatorItem]] = None
    
    # Pivot points
    pivot: Optional[PivotData] = None

    class Config:
        populate_by_name = True


class TechnicalAnalysisResponse(BaseModel):
    """Response wrapper for technical analysis."""
    symbol: str
    timeframe: str
    data: Optional[TechnicalAnalysisData] = None
    error: Optional[str] = None

"""Sector schemas for API responses."""

from typing import Optional, List
from pydantic import BaseModel, Field


class ICBCodeItem(BaseModel):
    """ICB code mapping item."""
    code: Optional[int] = Field(None, description="ICB code")
    en_sector: Optional[str] = Field(None, description="English sector name")
    vi_sector: Optional[str] = Field(None, description="Vietnamese sector name")
    icb_level: Optional[int] = Field(None, description="ICB level (1-4)")
    is_level1_custom: Optional[bool] = Field(None)

    class Config:
        populate_by_name = True


class SectorPerformance(BaseModel):
    """Sector performance metrics."""
    icb_code: int = Field(..., alias="icbCode", description="ICB sector code")
    market_cap: Optional[float] = Field(None, alias="marketCap", description="Market capitalization")
    weight_percent: Optional[float] = Field(None, alias="weightPercent", description="Weight in index (%)")
    last_close_index: Optional[float] = Field(None, alias="lastCloseIndex", description="Last closing index")
    last_20_day_index: Optional[List[float]] = Field(None, alias="last20DayIndex", description="20-day index values for sparkline")
    
    # Price changes
    percent_change_1d: Optional[float] = Field(None, alias="percentPriceChange1Day")
    percent_change_1w: Optional[float] = Field(None, alias="percentPriceChange1Week")
    percent_change_1m: Optional[float] = Field(None, alias="percentPriceChange1Month")
    percent_change_6m: Optional[float] = Field(None, alias="percentPriceChange6Month")
    percent_change_ytd: Optional[float] = Field(None, alias="percentPriceChangeYTD")
    percent_change_1y: Optional[float] = Field(None, alias="percentPriceChange1Year")
    percent_change_2y: Optional[float] = Field(None, alias="percentPriceChange2Year")
    percent_change_5y: Optional[float] = Field(None, alias="percentPriceChange5Year")

    class Config:
        populate_by_name = True


class SectorInfoResponse(BaseModel):
    """Sector information with ICB name mapping."""
    icb_code: int
    en_sector: Optional[str] = None
    vi_sector: Optional[str] = None
    icb_level: Optional[int] = None
    market_cap: Optional[float] = None
    weight_percent: Optional[float] = None
    last_close_index: Optional[float] = None
    last_20_day_index: Optional[List[float]] = None
    
    # Price changes
    percent_change_1d: Optional[float] = None
    percent_change_1w: Optional[float] = None
    percent_change_1m: Optional[float] = None
    percent_change_6m: Optional[float] = None
    percent_change_ytd: Optional[float] = None
    percent_change_1y: Optional[float] = None
    percent_change_2y: Optional[float] = None
    percent_change_5y: Optional[float] = None


class SectorRankingValue(BaseModel):
    """Single ranking value for a date."""
    date: str
    value: Optional[float] = None
    sector_trend: Optional[str] = Field(None, alias="sectorTrend")

    class Config:
        populate_by_name = True


class SectorRanking(BaseModel):
    """Sector ranking with daily values."""
    icb_code: int = Field(..., description="ICB sector code")
    en_sector: Optional[str] = None
    vi_sector: Optional[str] = None
    values: List[SectorRankingValue] = Field(default_factory=list)


class SectorCompany(BaseModel):
    """Company within a sector."""
    ticker: str
    company_name: Optional[str] = Field(None, alias="organShortNameVi")
    market_cap: Optional[float] = Field(None, alias="marketCap")
    latest_price: Optional[float] = Field(None, alias="latestPrice")
    percent_change: Optional[float] = Field(None, alias="percentPriceChange")
    
    # Valuation metrics
    ttm_pe: Optional[float] = Field(None, alias="ttmPe")
    ttm_pb: Optional[float] = Field(None, alias="ttmPb")
    ttm_eps: Optional[float] = Field(None, alias="ttmEps")
    
    # Profitability
    roe: Optional[float] = None
    roa: Optional[float] = None
    
    # Volume
    avg_volume_1m: Optional[float] = Field(None, alias="averageMatchVolume1Month")
    
    # Foreign
    foreign_room: Optional[float] = Field(None, alias="foreignRoom")
    foreign_ownership: Optional[float] = Field(None, alias="foreignOwnership")

    class Config:
        populate_by_name = True


class SectorCompaniesResponse(BaseModel):
    """Response for sector companies list."""
    icb_code: int
    en_sector: Optional[str] = None
    vi_sector: Optional[str] = None
    total_companies: int = 0
    companies: List[SectorCompany] = Field(default_factory=list)


class SectorIndexDataPoint(BaseModel):
    """Single data point for sector index history."""
    date: str
    value: Optional[float] = None


class SectorIndexHistory(BaseModel):
    """Sector index history for charting."""
    icb_code: int = Field(..., alias="icbCode")
    en_sector: Optional[str] = None
    vi_sector: Optional[str] = None
    data: List[SectorIndexDataPoint] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class TradingDatesResponse(BaseModel):
    """Trading dates response."""
    dates: List[str] = Field(default_factory=list)


class SectorListResponse(BaseModel):
    """List of sectors with full information."""
    total: int = 0
    icb_level: int = 2
    sectors: List[SectorInfoResponse] = Field(default_factory=list)


class SectorRankingResponse(BaseModel):
    """Sector ranking response."""
    total: int = 0
    icb_level: int = 2
    rankings: List[SectorRanking] = Field(default_factory=list)

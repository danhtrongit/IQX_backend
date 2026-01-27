"""Sector API endpoints."""

from typing import List
from fastapi import APIRouter, Query

from app.application.sector.services import get_sector_service
from app.application.sector.schemas import (
    SectorListResponse,
    SectorRankingResponse,
    SectorCompaniesResponse,
    SectorIndexHistory,
    TradingDatesResponse,
    ICBCodeItem,
)

router = APIRouter(prefix="/sector", tags=["sector"])


@router.get(
    "/information",
    response_model=SectorListResponse,
    summary="Get sector information",
    description="Get sector performance metrics including market cap, weight, and price changes over multiple timeframes."
)
async def get_sector_information(
    icb_level: int = Query(2, ge=1, le=4, description="ICB level (1=Industry, 2=Supersector, 3=Sector, 4=Subsector)")
):
    """
    Get sector information with performance metrics.
    
    Returns list of sectors with:
    - Market capitalization
    - Weight in index (%)
    - 20-day sparkline data
    - Price changes: 1D, 1W, 1M, 6M, YTD, 1Y, 2Y, 5Y
    """
    service = get_sector_service()
    return await service.get_sector_information(icb_level)


@router.get(
    "/ranking",
    response_model=SectorRankingResponse,
    summary="Get sector ranking",
    description="Get sector ranking with daily performance and trend information."
)
async def get_sector_ranking(
    icb_level: int = Query(2, ge=1, le=4, description="ICB level"),
    adtv: int = Query(3, ge=1, le=5, description="ADTV filter"),
    value: int = Query(3, ge=1, le=5, description="Value filter")
):
    """
    Get sector ranking with daily trends.
    
    Returns sectors ranked by performance with:
    - Daily values over the last 20 trading days
    - Sector trend indicators
    """
    service = get_sector_service()
    return await service.get_sector_ranking(icb_level, adtv, value)


@router.get(
    "/companies/{icb_code}",
    response_model=SectorCompaniesResponse,
    summary="Get sector companies",
    description="Get list of companies within a specific sector."
)
async def get_sector_companies(icb_code: int):
    """
    Get companies within a sector.
    
    Returns list of stocks with:
    - Ticker and company name
    - Market cap and latest price
    - Valuation metrics (P/E, P/B, EPS)
    - Profitability (ROE, ROA)
    - Average volume and foreign ownership
    """
    service = get_sector_service()
    return await service.get_sector_companies(icb_code)


@router.get(
    "/index-history",
    response_model=List[SectorIndexHistory],
    summary="Get sector index history",
    description="Get historical index values for specified sectors (for charting)."
)
async def get_sector_index_history(
    icb_codes: str = Query(..., description="Comma-separated ICB codes (e.g., '8300,5500,3500')"),
    icb_level: int = Query(2, ge=1, le=4, description="ICB level"),
    number_of_days: str = Query("ALL", description="Number of days or 'ALL'")
):
    """
    Get sector index history for charting.
    
    Returns historical price data for each sector.
    """
    codes = [int(c.strip()) for c in icb_codes.split(",") if c.strip().isdigit()]
    if not codes:
        return []
    
    service = get_sector_service()
    return await service.get_sector_index_history(codes, icb_level, number_of_days)


@router.get(
    "/trading-dates",
    response_model=TradingDatesResponse,
    summary="Get trading dates",
    description="Get list of recent trading dates."
)
async def get_trading_dates():
    """Get recent trading dates in YYYY-MM-DD format."""
    service = get_sector_service()
    return await service.get_trading_dates()


@router.get(
    "/icb-codes",
    response_model=List[ICBCodeItem],
    summary="Get ICB codes",
    description="Get mapping of ICB sector codes to names."
)
async def get_icb_codes():
    """Get all ICB codes with English and Vietnamese names."""
    service = get_sector_service()
    return await service.get_icb_codes()

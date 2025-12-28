
"""Market endpoints."""
from typing import Optional
from fastapi import APIRouter, Query

from app.application.market.dtos import (
    IndexResponse,
    MarketOverviewResponse,
    IndexHistoryRequest,
    IndexHistoryResponse,
    MarketEvaluationResponse
)
from app.application.market.services import MarketService
from app.core.cache import get_cache, CacheTTL, make_cache_key

router = APIRouter(prefix="/market", tags=["Market"])


def get_market_service() -> MarketService:
    """Create market service."""
    return MarketService()


@router.get("/overview", response_model=MarketOverviewResponse)
async def get_market_overview() -> MarketOverviewResponse:
    """
    Get market overview with all major indices.
    
    Returns:
    - VNINDEX
    - HNXINDEX
    - UPCOMINDEX
    - VN30
    
    Each index includes:
    - Current value, change, change percent
    - Open, high, low values
    - Total volume and value
    - Advances, declines, unchanged counts
    """
    cache = get_cache()
    cache_key = "market:overview"
    
    # Try cache first
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    # Fetch and cache
    service = get_market_service()
    result = await service.get_market_overview()
    await cache.set(cache_key, result, CacheTTL.MARKET_OVERVIEW)
    return result


@router.get("/indices/{index_code}", response_model=IndexResponse)
async def get_index(
    index_code: str,
) -> IndexResponse:
    """
    Get single index data.
    
    **Index codes:**
    - VNINDEX - VN-Index (HOSE)
    - HNXINDEX - HNX-Index
    - UPCOMINDEX - UPCOM-Index
    - VN30 - VN30 Index
    """
    cache = get_cache()
    cache_key = f"market:index:{index_code.upper()}"
    
    # Try cache first
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    # Fetch and cache
    service = get_market_service()
    result = await service.get_index(index_code)
    await cache.set(cache_key, result, CacheTTL.MARKET_OVERVIEW)
    return result


@router.get("/indices/{index_code}/history", response_model=IndexHistoryResponse)
async def get_index_history(
    index_code: str,
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    interval: str = Query("1D", description="Interval: 1D, 1W, 1M"),
) -> IndexHistoryResponse:
    """
    Get index historical data.
    
    - **index_code**: VNINDEX, HNXINDEX, UPCOMINDEX, VN30
    - **start**: Start date in YYYY-MM-DD format
    - **end**: End date (optional, defaults to today)
    - **interval**: Time interval (1D, 1W, 1M)
    """
    cache = get_cache()
    cache_key = f"market:history:{index_code.upper()}:{start}:{end}:{interval}"
    
    # Try cache first
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    # Fetch and cache
    service = get_market_service()
    request = IndexHistoryRequest(start=start, end=end, interval=interval)
    result = await service.get_index_history(index_code, request)
    await cache.set(cache_key, result, CacheTTL.HISTORICAL_RECENT)
    return result

@router.get("/evaluation", response_model=MarketEvaluationResponse)
async def get_market_evaluation(
    period: str = Query('day', description="period: day, week, month"),
    time_window: str = Query('1D', description="time window")
) -> MarketEvaluationResponse:
    """Get market evaluation (PE, PB)."""
    cache = get_cache()
    cache_key = f"market:evaluation:{period}:{time_window}"
    cached = await cache.get(cache_key)
    if cached:
        return cached
        
    service = get_market_service()
    result = await service.get_evaluation(period=period, time_window=time_window)
    await cache.set(cache_key, result, CacheTTL.COMMON_INFO)
    return result

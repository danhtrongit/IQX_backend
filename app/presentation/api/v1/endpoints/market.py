
"""Market endpoints."""
from typing import Optional
from fastapi import APIRouter, Query

from app.application.market.dtos import (
    IndexResponse,
    MarketOverviewResponse,
    IndexHistoryRequest,
    IndexHistoryResponse,
    MarketEvaluationResponse,
    AllocatedValueResponse,
    AllocatedICBResponse,
    AllocatedICBDetailResponse,
    IndexImpactResponse,
    TopProprietaryResponse,
    ForeignNetValueResponse
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


@router.get("/allocated-value", response_model=AllocatedValueResponse)
async def get_allocated_value(
    group: str = Query("HOSE", description="Market group: HOSE, HNX, UPCOME, ALL"),
    time_frame: str = Query("ONE_WEEK", description="Time frame: ONE_DAY, ONE_WEEK, ONE_MONTH, YTD, ONE_YEAR")
) -> AllocatedValueResponse:
    """
    Get allocated value (capital flow by sector).
    
    Data from Vietcap showing capital distribution across market sectors.
    
    **Note:** This API proxies to Vietcap's trading API. If data is empty,
    the frontend may need to call the Vietcap API directly from the browser
    (see /allocated-value-info for direct API details).
    
    **Parameters:**
    - **group**: Market group
        - HOSE: Ho Chi Minh Stock Exchange
        - HNX: Hanoi Stock Exchange
        - UPCOME: Unlisted Public Company Market
        - ALL: All markets combined
    - **time_frame**: Time period for calculation
        - ONE_DAY: 1 day
        - ONE_WEEK: 1 week
        - ONE_MONTH: 1 month
        - YTD: Year to date
        - ONE_YEAR: 1 year
    
    **Returns:**
    - Sector-wise capital allocation with values and percentages
    """
    cache = get_cache()
    cache_key = f"market:allocated_value:{group.upper()}:{time_frame.upper()}"
    
    cached = await cache.get(cache_key)
    if cached:
        return cached
    
    service = get_market_service()
    result = await service.get_allocated_value(group=group, time_frame=time_frame)
    
    # Only cache if we got data
    if result.count > 0:
        await cache.set(cache_key, result, CacheTTL.MARKET_OVERVIEW)
    
    return result


@router.get("/allocated-value-info")
async def get_allocated_value_info():
    """
    Get information for direct Vietcap API call from frontend.
    
    Use this if the /allocated-value endpoint returns empty data.
    The Vietcap API may block server-to-server calls but allows browser requests.
    """
    return {
        "url": "https://trading.vietcap.com.vn/api/market-watch/AllocatedValue/getAllocatedValue",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        "body_example": {
            "group": "HOSE",
            "timeFrame": "ONE_WEEK"
        },
        "parameters": {
            "group": {
                "type": "string",
                "options": ["HOSE", "HNX", "UPCOME", "ALL"],
                "description": "Market group"
            },
            "timeFrame": {
                "type": "string", 
                "options": ["ONE_DAY", "ONE_WEEK", "ONE_MONTH", "YTD", "ONE_YEAR"],
                "description": "Time period for calculation"
            }
        },
        "note": "This API may require browser-based calls due to WAF protection"
    }


@router.get("/allocated-icb", response_model=AllocatedICBResponse)
async def get_allocated_icb(
    group: str = Query("HOSE", description="Market group: HOSE, HNX, UPCOME, ALL"),
    time_frame: str = Query("ONE_WEEK", description="Time frame: ONE_DAY, ONE_WEEK, ONE_MONTH, YTD, ONE_YEAR")
) -> AllocatedICBResponse:
    """
    Get allocated ICB (sector allocation by industry).
    
    Data from Vietcap showing capital distribution across ICB sectors.
    
    **Parameters:**
    - **group**: Market group
        - HOSE: Ho Chi Minh Stock Exchange
        - HNX: Hanoi Stock Exchange
        - UPCOME: Unlisted Public Company Market
        - ALL: All markets combined
    - **time_frame**: Time period for calculation
        - ONE_DAY: 1 day
        - ONE_WEEK: 1 week
        - ONE_MONTH: 1 month
        - YTD: Year to date
        - ONE_YEAR: 1 year
    
    **Returns:**
    - List of ICB sectors with:
        - icb_code: ICB industry code
        - icb_change_percent: % change
        - total_price_change: Total price change
        - total_market_cap: Market cap
        - total_value: Trading value
        - total_stock_increase/decrease/no_change: Stock counts
        - icb_code_parent: Parent ICB code (null for top level)
    """
    cache = get_cache()
    cache_key = f"market:allocated_icb:{group.upper()}:{time_frame.upper()}"
    
    cached = await cache.get(cache_key)
    if cached:
        return cached
    
    service = get_market_service()
    result = await service.get_allocated_icb(group=group, time_frame=time_frame)
    
    # Only cache if we got data
    if result.count > 0:
        await cache.set(cache_key, result, CacheTTL.MARKET_OVERVIEW)
    
    return result


@router.get("/allocated-icb-detail", response_model=AllocatedICBDetailResponse)
async def get_allocated_icb_detail(
    icb_code: int = Query(..., description="ICB code to get details for (e.g., 9500 for Technology)"),
    group: str = Query("HOSE", description="Market group: HOSE, HNX, UPCOME, ALL"),
    time_frame: str = Query("ONE_WEEK", description="Time frame: ONE_DAY, ONE_WEEK, ONE_MONTH, YTD, ONE_YEAR")
) -> AllocatedICBDetailResponse:
    """
    Get allocated ICB detail (stocks within a sector).
    
    Data from Vietcap showing individual stocks within an ICB sector.
    
    **Parameters:**
    - **icb_code**: ICB code (required)
        - 9500: Công nghệ Thông tin (Technology)
        - 8300: Ngân hàng (Banks)
        - 8600: Bất động sản (Real Estate)
        - See /allocated-icb for all available codes
    - **group**: Market group
    - **time_frame**: Time period
    
    **Returns:**
    - Sector summary (icb_code, change %, market cap)
    - stocks: List of stocks with symbol, prices, volume, market cap
    """
    cache = get_cache()
    cache_key = f"market:allocated_icb_detail:{icb_code}:{group.upper()}:{time_frame.upper()}"
    
    cached = await cache.get(cache_key)
    if cached:
        return cached
    
    service = get_market_service()
    result = await service.get_allocated_icb_detail(
        group=group, 
        time_frame=time_frame,
        icb_code=icb_code
    )
    
    # Only cache if we got stocks
    if result.stocks:
        await cache.set(cache_key, result, CacheTTL.MARKET_OVERVIEW)
    
    return result


@router.get("/index-impact", response_model=IndexImpactResponse)
async def get_index_impact(
    group: str = Query("ALL", description="Market group: HOSE, HNX, UPCOME, ALL"),
    time_frame: str = Query("ONE_WEEK", description="Time frame: ONE_DAY, ONE_WEEK, ONE_MONTH, YTD, ONE_YEAR")
) -> IndexImpactResponse:
    """
    Get index impact (market leading stocks).
    
    Data from Vietcap showing stocks with highest impact on market indices.
    
    **Parameters:**
    - **group**: Market group
    - **time_frame**: Time period
    
    **Returns:**
    - **top_up**: Stocks pulling market UP (positive impact on index)
    - **top_down**: Stocks pulling market DOWN (negative impact on index)
    
    Each stock includes:
    - symbol, company name (VI & EN)
    - impact: Points of impact on index
    - match_price, ref_price
    """
    cache = get_cache()
    cache_key = f"market:index_impact:{group.upper()}:{time_frame.upper()}"
    
    cached = await cache.get(cache_key)
    if cached:
        return cached
    
    service = get_market_service()
    result = await service.get_index_impact(group=group, time_frame=time_frame)
    
    # Only cache if we got data
    if result.top_up or result.top_down:
        await cache.set(cache_key, result, CacheTTL.MARKET_OVERVIEW)
    
    return result


@router.get("/top-proprietary", response_model=TopProprietaryResponse)
async def get_top_proprietary(
    exchange: str = Query("ALL", description="Exchange: HOSE, HNX, UPCOM, ALL"),
    time_frame: str = Query("ONE_WEEK", description="Time frame: ONE_DAY, ONE_WEEK, ONE_MONTH, YTD, ONE_YEAR")
) -> TopProprietaryResponse:
    """
    Get top proprietary trading (self-trading by securities companies).
    
    **Parameters:**
    - **exchange**: Stock exchange
    - **time_frame**: Time period
    
    **Returns:**
    - **buy**: Stocks with top proprietary buying
    - **sell**: Stocks with top proprietary selling
    """
    cache = get_cache()
    cache_key = f"market:top_proprietary:{exchange.upper()}:{time_frame.upper()}"
    
    cached = await cache.get(cache_key)
    if cached:
        return cached
    
    service = get_market_service()
    result = await service.get_top_proprietary(exchange=exchange, time_frame=time_frame)
    
    if result.buy or result.sell:
        await cache.set(cache_key, result, CacheTTL.MARKET_OVERVIEW)
    
    return result


@router.get("/foreign-net-value", response_model=ForeignNetValueResponse)
async def get_foreign_net_value(
    group: str = Query("ALL", description="Market group: HOSE, HNX, UPCOME, ALL"),
    time_frame: str = Query("ONE_WEEK", description="Time frame: ONE_DAY, ONE_WEEK, ONE_MONTH, YTD, ONE_YEAR")
) -> ForeignNetValueResponse:
    """
    Get foreign net value (foreign investor buying/selling).
    
    **Parameters:**
    - **group**: Market group
    - **time_frame**: Time period
    
    **Returns:**
    - **net_buy**: Top stocks with foreign net buying
    - **net_sell**: Top stocks with foreign net selling
    
    Each stock includes: net value, buy value, sell value, prices
    """
    cache = get_cache()
    cache_key = f"market:foreign_net_value:{group.upper()}:{time_frame.upper()}"
    
    cached = await cache.get(cache_key)
    if cached:
        return cached
    
    service = get_market_service()
    result = await service.get_foreign_net_value(group=group, time_frame=time_frame)
    
    if result.net_buy or result.net_sell:
        await cache.set(cache_key, result, CacheTTL.MARKET_OVERVIEW)
    
    return result

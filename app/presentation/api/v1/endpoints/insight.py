"""Insight/Analysis endpoints with async optimization."""
from typing import Optional
from fastapi import APIRouter, Query

from app.application.insight.dtos import (
    TopForeignResponse,
    TopStockResponse,
    ProprietaryTradingResponse,
    ForeignTradingResponse,
    OrderStatsResponse,
    SideStatsResponse,
    InsiderTradingResponse,
)
from app.application.insight.services import InsightService, TradingInsightService
from app.infrastructure.vnstock.insight_provider import (
    VnstockInsightProvider,
    VnstockTradingInsightProvider,
)
from app.core.cache import get_cache, CacheTTL
from app.core.async_utils import run_sync

router = APIRouter(prefix="/insight", tags=["Insight"])

# Singleton providers
_insight_provider = None
_trading_insight_provider = None


def _get_insight_provider() -> VnstockInsightProvider:
    global _insight_provider
    if _insight_provider is None:
        _insight_provider = VnstockInsightProvider()
    return _insight_provider


def _get_trading_insight_provider() -> VnstockTradingInsightProvider:
    global _trading_insight_provider
    if _trading_insight_provider is None:
        _trading_insight_provider = VnstockTradingInsightProvider()
    return _trading_insight_provider


def get_insight_service() -> InsightService:
    return InsightService(data_provider=_get_insight_provider())


def get_trading_insight_service() -> TradingInsightService:
    return TradingInsightService(data_provider=_get_trading_insight_provider())


# === Top Foreign APIs ===

@router.get("/top/foreign-buy", response_model=TopForeignResponse)
async def get_top_foreign_buy(
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD), default today"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
) -> TopForeignResponse:
    """Get top stocks with highest foreign net buy value."""
    cache = get_cache()
    cache_key = f"insight:foreign_buy:{date}:{limit}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_insight_service()
    result = await run_sync(service.get_top_foreign_buy, date=date, limit=limit)
    await cache.set(cache_key, result, CacheTTL.TOP_STOCKS)
    return result


@router.get("/top/foreign-sell", response_model=TopForeignResponse)
async def get_top_foreign_sell(
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD), default today"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
) -> TopForeignResponse:
    """Get top stocks with highest foreign net sell value."""
    cache = get_cache()
    cache_key = f"insight:foreign_sell:{date}:{limit}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_insight_service()
    result = await run_sync(service.get_top_foreign_sell, date=date, limit=limit)
    await cache.set(cache_key, result, CacheTTL.TOP_STOCKS)
    return result


# === Top Stock APIs ===

@router.get("/top/gainer", response_model=TopStockResponse)
async def get_top_gainer(
    index: str = Query("VNINDEX", description="Index: VNINDEX, HNXINDEX, UPCOMINDEX"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
) -> TopStockResponse:
    """Get top gaining stocks."""
    cache = get_cache()
    cache_key = f"insight:gainer:{index}:{limit}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_insight_service()
    result = await run_sync(service.get_top_gainer, index=index, limit=limit)
    await cache.set(cache_key, result, CacheTTL.TOP_STOCKS)
    return result


@router.get("/top/loser", response_model=TopStockResponse)
async def get_top_loser(
    index: str = Query("VNINDEX", description="Index: VNINDEX, HNXINDEX, UPCOMINDEX"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
) -> TopStockResponse:
    """Get top losing stocks."""
    cache = get_cache()
    cache_key = f"insight:loser:{index}:{limit}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_insight_service()
    result = await run_sync(service.get_top_loser, index=index, limit=limit)
    await cache.set(cache_key, result, CacheTTL.TOP_STOCKS)
    return result


@router.get("/top/value", response_model=TopStockResponse)
async def get_top_value(
    index: str = Query("VNINDEX", description="Index: VNINDEX, HNXINDEX, UPCOMINDEX"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
) -> TopStockResponse:
    """Get top stocks by trading value."""
    cache = get_cache()
    cache_key = f"insight:value:{index}:{limit}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_insight_service()
    result = await run_sync(service.get_top_value, index=index, limit=limit)
    await cache.set(cache_key, result, CacheTTL.TOP_STOCKS)
    return result


@router.get("/top/volume", response_model=TopStockResponse)
async def get_top_volume(
    index: str = Query("VNINDEX", description="Index: VNINDEX, HNXINDEX, UPCOMINDEX"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
) -> TopStockResponse:
    """Get top stocks by abnormal volume."""
    cache = get_cache()
    cache_key = f"insight:volume:{index}:{limit}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_insight_service()
    result = await run_sync(service.get_top_volume, index=index, limit=limit)
    await cache.set(cache_key, result, CacheTTL.TOP_STOCKS)
    return result


@router.get("/top/deal", response_model=TopStockResponse)
async def get_top_deal(
    index: str = Query("VNINDEX", description="Index: VNINDEX, HNXINDEX, UPCOMINDEX"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
) -> TopStockResponse:
    """Get top stocks by block deal volume."""
    cache = get_cache()
    cache_key = f"insight:deal:{index}:{limit}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_insight_service()
    result = await run_sync(service.get_top_deal, index=index, limit=limit)
    await cache.set(cache_key, result, CacheTTL.TOP_STOCKS)
    return result


# === Per-Symbol Trading Insight APIs ===

@router.get("/{symbol}/proprietary", response_model=ProprietaryTradingResponse)
async def get_proprietary_trading(
    symbol: str,
    start: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(30, ge=1, le=100, description="Number of results"),
) -> ProprietaryTradingResponse:
    """Get proprietary trading history for a symbol."""
    cache = get_cache()
    cache_key = f"insight:proprietary:{symbol.upper()}:{start}:{end}:{limit}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_trading_insight_service()
    result = await run_sync(
        service.get_proprietary_trading, symbol=symbol, start=start, end=end, limit=limit
    )
    await cache.set(cache_key, result, CacheTTL.HISTORICAL_RECENT)
    return result


@router.get("/{symbol}/foreign", response_model=ForeignTradingResponse)
async def get_foreign_trading(
    symbol: str,
    start: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(30, ge=1, le=100, description="Number of results"),
) -> ForeignTradingResponse:
    """Get foreign trading history for a symbol."""
    cache = get_cache()
    cache_key = f"insight:foreign:{symbol.upper()}:{start}:{end}:{limit}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_trading_insight_service()
    result = await run_sync(
        service.get_foreign_trading, symbol=symbol, start=start, end=end, limit=limit
    )
    await cache.set(cache_key, result, CacheTTL.HISTORICAL_RECENT)
    return result


@router.get("/{symbol}/orders", response_model=OrderStatsResponse)
async def get_order_stats(symbol: str) -> OrderStatsResponse:
    """Get order statistics (count/volume by type)."""
    cache = get_cache()
    cache_key = f"insight:orders:{symbol.upper()}"
    
    cached = await cache.get(cache_key)
    if cached:
        return cached

    service = get_trading_insight_service()
    result = await run_sync(service.get_order_stats, symbol)
    await cache.set(cache_key, result, CacheTTL.INTRADAY)
    return result


@router.get("/{symbol}/sides", response_model=SideStatsResponse)
async def get_side_stats(symbol: str) -> SideStatsResponse:
    """Get side statistics (Buy/Sell volume)."""
    cache = get_cache()
    cache_key = f"insight:sides:{symbol.upper()}"

    cached = await cache.get(cache_key)
    if cached:
        return cached

    service = get_trading_insight_service()
    result = await run_sync(service.get_side_stats, symbol)
    await cache.set(cache_key, result, CacheTTL.INTRADAY)
    return result


@router.get("/{symbol}/insider", response_model=InsiderTradingResponse)
async def get_insider_trading(
    symbol: str,
    start: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(30, ge=1, le=100, description="Number of results"),
) -> InsiderTradingResponse:
    """Get insider trading history for a symbol (giao dich noi bo)."""
    cache = get_cache()
    cache_key = f"insight:insider:{symbol.upper()}:{start}:{end}:{limit}"

    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    service = get_trading_insight_service()
    result = await run_sync(
        service.get_insider_trading, symbol=symbol, start=start, end=end, limit=limit
    )
    await cache.set(cache_key, result, CacheTTL.HISTORICAL_RECENT)
    return result

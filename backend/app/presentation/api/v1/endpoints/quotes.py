"""Quote endpoints with async optimization."""
from typing import Optional
from fastapi import APIRouter, Query, Body

from app.application.quote.dtos import (
    HistoryRequest,
    IntradayRequest,
    PriceBoardRequest,
    TradingStatsRequest,
    HistoryResponse,
    IntradayResponse,
    PriceBoardResponse,
    PriceDepthResponse,
    TradingStatsResponse,
)
from app.application.quote.services import QuoteService
from app.infrastructure.vnstock.quote_provider import VnstockQuoteProvider
from app.core.cache import get_cache, CacheTTL
from app.core.async_utils import run_sync

router = APIRouter(prefix="/quotes", tags=["Quotes"])

# Singleton provider to avoid repeated initialization
_quote_provider: Optional[VnstockQuoteProvider] = None


def _get_provider() -> VnstockQuoteProvider:
    """Get singleton quote provider."""
    global _quote_provider
    if _quote_provider is None:
        _quote_provider = VnstockQuoteProvider()
    return _quote_provider


def get_quote_service() -> QuoteService:
    """Create quote service with dependencies."""
    return QuoteService(data_provider=_get_provider())


@router.get("/{symbol}/history", response_model=HistoryResponse)
async def get_history(
    symbol: str,
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    interval: str = Query("1D", description="Interval: 1m, 5m, 15m, 30m, 1H, 1D, 1W, 1M"),
    count_back: Optional[int] = Query(None, ge=1, le=5000, description="Number of candles"),
) -> HistoryResponse:
    """Get historical OHLCV data for a symbol."""
    cache = get_cache()
    cache_key = f"quotes:history:{symbol.upper()}:{start}:{end}:{interval}:{count_back}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_quote_service()
    request = HistoryRequest(start=start, end=end, interval=interval, count_back=count_back)
    
    result = await run_sync(service.get_history, symbol, request)
    await cache.set(cache_key, result, CacheTTL.HISTORICAL_RECENT)
    return result


@router.get("/{symbol}/intraday", response_model=IntradayResponse)
async def get_intraday(
    symbol: str,
    page_size: int = Query(100, ge=1, le=5000, description="Number of trades"),
    last_time: Optional[str] = Query(None, description="Get trades after this time"),
) -> IntradayResponse:
    """Get intraday trades for a symbol."""
    cache = get_cache()
    cache_key = f"quotes:intraday:{symbol.upper()}:{page_size}:{last_time}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_quote_service()
    request = IntradayRequest(page_size=page_size, last_time=last_time)
    
    result = await run_sync(service.get_intraday, symbol, request)
    await cache.set(cache_key, result, CacheTTL.INTRADAY)
    return result


@router.post("/price-board", response_model=PriceBoardResponse)
async def get_price_board(
    request: PriceBoardRequest = Body(...),
) -> PriceBoardResponse:
    """Get current price board for multiple symbols."""
    cache = get_cache()
    sorted_symbols = sorted([s.upper() for s in request.symbols])
    cache_key = f"quotes:price_board:{','.join(sorted_symbols)}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_quote_service()
    result = await run_sync(service.get_price_board, request)
    await cache.set(cache_key, result, CacheTTL.PRICE_BOARD)
    return result


@router.get("/{symbol}/depth", response_model=PriceDepthResponse)
async def get_price_depth(symbol: str) -> PriceDepthResponse:
    """Get price depth for a symbol."""
    cache = get_cache()
    cache_key = f"quotes:depth:{symbol.upper()}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_quote_service()
    result = await run_sync(service.get_price_depth, symbol)
    await cache.set(cache_key, result, CacheTTL.INTRADAY)
    return result


@router.get("/{symbol}/trading-stats", response_model=TradingStatsResponse)
async def get_trading_stats(
    symbol: str,
    resolution: str = Query("1D", description="Resolution: 1D, 1W, 1M"),
    start: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000),
) -> TradingStatsResponse:
    """Get trading statistics for a symbol."""
    cache = get_cache()
    cache_key = f"quotes:trading_stats:{symbol.upper()}:{resolution}:{start}:{end}:{limit}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_quote_service()
    request = TradingStatsRequest(resolution=resolution, start=start, end=end, limit=limit)
    
    result = await run_sync(service.get_trading_stats, symbol, request)
    await cache.set(cache_key, result, CacheTTL.HISTORICAL_RECENT)
    return result

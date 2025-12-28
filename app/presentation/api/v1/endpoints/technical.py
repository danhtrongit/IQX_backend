"""Technical Analysis API endpoints with async optimization."""
from fastapi import APIRouter, Query, HTTPException

from app.application.technical.dtos import (
    TechnicalTimeframe,
    TechnicalAnalysisResponse,
)
from app.application.technical.services import TechnicalAnalysisService
from app.infrastructure.vietcap.technical_provider import VietcapTechnicalProvider
from app.core.cache import get_cache, CacheTTL
from app.core.async_utils import run_sync

router = APIRouter(prefix="/technical", tags=["Technical Analysis"])

# Singleton provider
_technical_provider = None


def _get_provider() -> VietcapTechnicalProvider:
    global _technical_provider
    if _technical_provider is None:
        _technical_provider = VietcapTechnicalProvider()
    return _technical_provider


def get_technical_service() -> TechnicalAnalysisService:
    return TechnicalAnalysisService(data_provider=_get_provider())


@router.get("/{symbol}", response_model=TechnicalAnalysisResponse)
async def get_technical_analysis(
    symbol: str,
    timeframe: TechnicalTimeframe = Query(
        TechnicalTimeframe.ONE_DAY,
        description="Timeframe: ONE_HOUR, ONE_DAY, ONE_WEEK"
    ),
) -> TechnicalAnalysisResponse:
    """
    Get technical analysis for a stock symbol.

    Returns technical indicators including:
    - Gauge Summary: Overall BUY/NEUTRAL/SELL signal with rating
    - Moving Averages: SMA, EMA, VWMA with various periods
    - Oscillators: RSI, MACD, Stochastic, CCI, etc.
    - Pivot Points: Classic, Fibonacci, Camarilla, Woodie, DeMark
    """
    cache = get_cache()
    cache_key = f"technical:{symbol.upper()}:{timeframe.value}"

    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    service = get_technical_service()
    result = await run_sync(
        service.get_technical_analysis, symbol=symbol, timeframe=timeframe.value
    )

    if result.error:
        raise HTTPException(status_code=503, detail=result.error)

    await cache.set(cache_key, result, CacheTTL.TECHNICAL_ANALYSIS)
    return result

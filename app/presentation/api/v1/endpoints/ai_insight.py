"""AI Insight API endpoints."""
from fastapi import APIRouter, Query, HTTPException

from sqlalchemy import text

from app.application.ai_insight.dtos import (
    AIInsightRequest,
    AIInsightResponse,
    OHLCDataPoint,
)
from app.application.ai_insight.services import AIInsightService
from app.infrastructure.db.session import async_session_factory
from app.core.cache import get_cache, CacheTTL
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ai-insight", tags=["AI Insight"])

# Configuration for Gemini proxy
GEMINI_PROXY_URL = "http://43.228.214.64:8317/v1/chat/completions"
GEMINI_API_KEY = "sk-ucc-m1xMHkNs3BRXUo0M3K2CZUaADGBeCIZWBWQsftA7h"
GEMINI_MODEL = "gemini-claude-opus-4-5-thinking"

# Singleton service
_ai_insight_service = None


def _get_service() -> AIInsightService:
    global _ai_insight_service
    if _ai_insight_service is None:
        _ai_insight_service = AIInsightService(
            proxy_url=GEMINI_PROXY_URL,
            api_key=GEMINI_API_KEY,
            model=GEMINI_MODEL,
        )
    return _ai_insight_service


async def _get_ohlc_data(symbol: str, days: int = 200) -> list[OHLCDataPoint]:
    """Fetch OHLC data with MA values from database."""
    async with async_session_factory() as session:
        query = text("""
            SELECT
                trade_date, open, high, low, close, volume,
                ma10, ma20, ma30, ma100, ma200,
                vol_ma10, vol_ma20, vol_ma30, vol_ma100, vol_ma200
            FROM stock_ohlc_daily
            WHERE symbol = :symbol
            ORDER BY trade_date DESC
            LIMIT :limit
        """)

        result = await session.execute(query, {"symbol": symbol.upper(), "limit": days})
        rows = result.fetchall()

        if not rows:
            return []

        # Reverse to get chronological order (oldest first)
        rows = list(reversed(rows))

        data_points = []
        for row in rows:
            data_points.append(OHLCDataPoint(
                trade_date=str(row[0]),
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=int(row[5]),
                ma10=float(row[6]) if row[6] else None,
                ma20=float(row[7]) if row[7] else None,
                ma30=float(row[8]) if row[8] else None,
                ma100=float(row[9]) if row[9] else None,
                ma200=float(row[10]) if row[10] else None,
                vol_ma10=int(row[11]) if row[11] else None,
                vol_ma20=int(row[12]) if row[12] else None,
                vol_ma30=int(row[13]) if row[13] else None,
                vol_ma100=int(row[14]) if row[14] else None,
                vol_ma200=int(row[15]) if row[15] else None,
            ))

        return data_points


@router.get("/{symbol}", response_model=AIInsightResponse)
async def get_ai_insight(
    symbol: str,
    period: int = Query(
        20,
        description="Analysis period: 10, 20, 30, 100, or 200 days",
        ge=10,
        le=200,
    ),
) -> AIInsightResponse:
    """
    Get AI-powered technical analysis insight for a stock symbol.

    Uses Gemini AI to analyze:
    - OHLCV data for the specified period
    - Moving averages (MA10, MA20, MA30, MA100, MA200)
    - Volume averages (10, 20, 30, 100, 200 sessions)
    - Current candlestick pattern

    Returns:
    - Description of current technical situation
    - Buy price and conditions
    - Stop-loss price and conditions
    - Take-profit price and conditions
    """
    cache = get_cache()
    cache_key = f"ai_insight:{symbol.upper()}:{period}"

    # Check cache first
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    # Fetch OHLC data from database
    ohlc_data = await _get_ohlc_data(symbol, days=200)

    if not ohlc_data:
        return AIInsightResponse(
            symbol=symbol.upper(),
            period=period,
            error="Không có dữ liệu OHLC. Vui lòng đồng bộ dữ liệu trước."
        )

    # Get AI insight
    service = _get_service()
    request = AIInsightRequest(period=period)
    result = await service.get_insight(symbol.upper(), ohlc_data, request)

    # Cache result for 30 minutes
    if not result.error:
        await cache.set(cache_key, result, ttl=1800)

    return result


@router.get("/{symbol}/pattern", response_model=dict)
async def get_candlestick_pattern(symbol: str) -> dict:
    """
    Get current candlestick pattern for a stock symbol.

    Returns the detected pattern name in Vietnamese.
    """
    from app.application.ai_insight.services import CandlestickPatternDetector

    ohlc_data = await _get_ohlc_data(symbol, days=10)

    if not ohlc_data:
        return {"symbol": symbol.upper(), "pattern": None, "error": "Không có dữ liệu"}

    detector = CandlestickPatternDetector()
    pattern = detector.detect_pattern(ohlc_data)

    return {
        "symbol": symbol.upper(),
        "pattern": pattern,
        "current_price": ohlc_data[-1].close if ohlc_data else None,
    }

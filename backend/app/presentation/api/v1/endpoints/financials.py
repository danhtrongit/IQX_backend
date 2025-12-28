"""Financial endpoints with async optimization."""
from fastapi import APIRouter, Query

from app.application.financial.dtos import (
    FinancialRequest,
    RatioRequest,
    FinancialReportResponse,
    RatioResponse,
)
from app.application.financial.services import FinancialService
from app.infrastructure.vnstock.financial_provider import VnstockFinancialProvider
from app.core.cache import get_cache, CacheTTL
from app.core.async_utils import run_sync

router = APIRouter(prefix="/financials", tags=["Financials"])

# Singleton provider
_financial_provider = None


def _get_provider() -> VnstockFinancialProvider:
    global _financial_provider
    if _financial_provider is None:
        _financial_provider = VnstockFinancialProvider()
    return _financial_provider


def get_financial_service() -> FinancialService:
    return FinancialService(data_provider=_get_provider())


@router.get("/{symbol}/balance-sheet", response_model=FinancialReportResponse)
async def get_balance_sheet(
    symbol: str,
    period: str = Query("quarter", description="Period: quarter or year"),
    lang: str = Query("vi", description="Language: vi or en"),
    limit: int = Query(20, ge=1, le=100, description="Number of periods"),
) -> FinancialReportResponse:
    """Get balance sheet for a symbol."""
    cache = get_cache()
    cache_key = f"financials:balance_sheet:{symbol.upper()}:{period}:{lang}:{limit}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_financial_service()
    request = FinancialRequest(period=period, lang=lang, limit=limit)
    result = await run_sync(service.get_balance_sheet, symbol, request)
    await cache.set(cache_key, result, CacheTTL.FINANCIALS)
    return result


@router.get("/{symbol}/income-statement", response_model=FinancialReportResponse)
async def get_income_statement(
    symbol: str,
    period: str = Query("quarter", description="Period: quarter or year"),
    lang: str = Query("vi", description="Language: vi or en"),
    limit: int = Query(20, ge=1, le=100, description="Number of periods"),
) -> FinancialReportResponse:
    """Get income statement for a symbol."""
    cache = get_cache()
    cache_key = f"financials:income_statement:{symbol.upper()}:{period}:{lang}:{limit}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_financial_service()
    request = FinancialRequest(period=period, lang=lang, limit=limit)
    result = await run_sync(service.get_income_statement, symbol, request)
    await cache.set(cache_key, result, CacheTTL.FINANCIALS)
    return result


@router.get("/{symbol}/cash-flow", response_model=FinancialReportResponse)
async def get_cash_flow(
    symbol: str,
    period: str = Query("quarter", description="Period: quarter or year"),
    lang: str = Query("vi", description="Language: vi or en"),
    limit: int = Query(20, ge=1, le=100, description="Number of periods"),
) -> FinancialReportResponse:
    """Get cash flow statement for a symbol."""
    cache = get_cache()
    cache_key = f"financials:cash_flow:{symbol.upper()}:{period}:{lang}:{limit}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_financial_service()
    request = FinancialRequest(period=period, lang=lang, limit=limit)
    result = await run_sync(service.get_cash_flow, symbol, request)
    await cache.set(cache_key, result, CacheTTL.FINANCIALS)
    return result


@router.get("/{symbol}/ratio", response_model=RatioResponse)
async def get_ratio(
    symbol: str,
    period: str = Query("quarter", description="Period: quarter or year"),
    limit: int = Query(20, ge=1, le=100, description="Number of periods"),
) -> RatioResponse:
    """Get financial ratios for a symbol."""
    cache = get_cache()
    cache_key = f"financials:ratio:{symbol.upper()}:{period}:{limit}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_financial_service()
    request = RatioRequest(period=period, limit=limit)
    result = await run_sync(service.get_ratio, symbol, request)
    await cache.set(cache_key, result, CacheTTL.FINANCIALS)
    return result

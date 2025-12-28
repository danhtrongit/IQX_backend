"""Company endpoints with async optimization."""
from fastapi import APIRouter, Query

from app.application.financial.dtos import (
    CompanyOverviewResponse,
    ShareholdersResponse,
    OfficersResponse,
    EventsResponse,
    NewsResponse,
    StockDetailResponse,
    AnalysisReportResponse,
)
from app.application.financial.services import CompanyService
from app.infrastructure.vnstock.financial_provider import VnstockCompanyProvider
from app.core.cache import get_cache, CacheTTL
from app.core.async_utils import run_sync

router = APIRouter(prefix="/company", tags=["Company"])

# Singleton provider
_company_provider = None


def _get_provider() -> VnstockCompanyProvider:
    global _company_provider
    if _company_provider is None:
        _company_provider = VnstockCompanyProvider()
    return _company_provider


def get_company_service() -> CompanyService:
    return CompanyService(data_provider=_get_provider())


@router.get("/{symbol}/overview", response_model=CompanyOverviewResponse)
async def get_overview(symbol: str) -> CompanyOverviewResponse:
    """Get company overview."""
    cache = get_cache()
    cache_key = f"company:overview:{symbol.upper()}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_company_service()
    result = await run_sync(service.get_overview, symbol)
    await cache.set(cache_key, result, CacheTTL.COMPANY_OVERVIEW)
    return result


@router.get("/{symbol}/shareholders", response_model=ShareholdersResponse)
async def get_shareholders(symbol: str) -> ShareholdersResponse:
    """Get major shareholders."""
    cache = get_cache()
    cache_key = f"company:shareholders:{symbol.upper()}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_company_service()
    result = await run_sync(service.get_shareholders, symbol)
    await cache.set(cache_key, result, CacheTTL.COMPANY_INFO)
    return result


@router.get("/{symbol}/officers", response_model=OfficersResponse)
async def get_officers(
    symbol: str,
    filter_by: str = Query("working", description="Filter: working, resigned, all"),
) -> OfficersResponse:
    """Get company officers."""
    cache = get_cache()
    cache_key = f"company:officers:{symbol.upper()}:{filter_by}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_company_service()
    result = await run_sync(service.get_officers, symbol, filter_by)
    await cache.set(cache_key, result, CacheTTL.OFFICERS)
    return result


@router.get("/{symbol}/events", response_model=EventsResponse)
async def get_events(symbol: str) -> EventsResponse:
    """Get company events."""
    cache = get_cache()
    cache_key = f"company:events:{symbol.upper()}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_company_service()
    result = await run_sync(service.get_events, symbol)
    await cache.set(cache_key, result, CacheTTL.COMPANY_INFO)
    return result


@router.get("/{symbol}/news", response_model=NewsResponse)
async def get_news(symbol: str) -> NewsResponse:
    """Get company news."""
    cache = get_cache()
    cache_key = f"company:news:{symbol.upper()}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_company_service()
    result = await run_sync(service.get_news, symbol)
    await cache.set(cache_key, result, CacheTTL.HISTORICAL_RECENT)
    return result


@router.get("/{symbol}/detail", response_model=StockDetailResponse)
async def get_stock_detail(symbol: str) -> StockDetailResponse:
    """Get stock detail for stock detail page."""
    cache = get_cache()
    cache_key = f"company:detail:{symbol.upper()}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_company_service()
    result = await run_sync(service.get_stock_detail, symbol)
    await cache.set(cache_key, result, CacheTTL.TOP_STOCKS)
    return result


@router.get("/{symbol}/analysis-reports", response_model=AnalysisReportResponse)
async def get_analysis_reports(
    symbol: str,
    page: int = Query(0, ge=0, description="Page number (0-indexed)"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> AnalysisReportResponse:
    """Get analysis reports for a company."""
    cache = get_cache()
    cache_key = f"company:analysis_reports:{symbol.upper()}:{page}:{size}"
    
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    service = get_company_service()
    result = await run_sync(service.get_analysis_reports, symbol, page=page, size=size)
    await cache.set(cache_key, result, CacheTTL.ANALYSIS_REPORTS)
    return result

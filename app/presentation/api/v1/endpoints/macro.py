"""Macro endpoints for Vietnamese macroeconomic data."""
from fastapi import APIRouter, Query

from app.application.macro.dtos import (
    GDPResponse,
    CPIResponse,
    ExchangeRateResponse,
    ImportExportResponse,
    FDIResponse,
    MoneySupplyResponse,
)
from app.application.macro.services import MacroService
from app.core.cache import get_cache, CacheTTL

router = APIRouter(prefix="/macro", tags=["Macro"])


def get_macro_service() -> MacroService:
    """Create macro service."""
    return MacroService()


@router.get("/gdp", response_model=GDPResponse)
async def get_gdp(
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
) -> GDPResponse:
    """
    Get Vietnam GDP (Gross Domestic Product) data.

    Returns historical GDP data including:
    - Report time/period
    - GDP value
    - Growth rate
    - Source information

    **Parameters:**
    - **limit**: Number of records to return (default: 20, max: 100)
    """
    cache = get_cache()
    cache_key = f"macro:gdp:{limit}"

    # Try cache first
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    # Fetch and cache
    service = get_macro_service()
    result = await service.get_gdp(limit=limit)
    await cache.set(cache_key, result, CacheTTL.MACRO)
    return result


@router.get("/cpi", response_model=CPIResponse)
async def get_cpi(
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
) -> CPIResponse:
    """
    Get Vietnam CPI (Consumer Price Index) data.

    Returns historical CPI/inflation data including:
    - Report time/period
    - CPI value
    - Inflation rate
    - Category breakdown

    **Parameters:**
    - **limit**: Number of records to return (default: 20, max: 100)
    """
    cache = get_cache()
    cache_key = f"macro:cpi:{limit}"

    # Try cache first
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    # Fetch and cache
    service = get_macro_service()
    result = await service.get_cpi(limit=limit)
    await cache.set(cache_key, result, CacheTTL.MACRO)
    return result


@router.get("/exchange-rate", response_model=ExchangeRateResponse)
async def get_exchange_rate(
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
) -> ExchangeRateResponse:
    """
    Get USD/VND exchange rate data.

    Returns historical exchange rate data including:
    - Report time/period
    - Exchange rate value
    - Central bank rates
    - Commercial bank rates

    **Parameters:**
    - **limit**: Number of records to return (default: 20, max: 100)
    """
    cache = get_cache()
    cache_key = f"macro:exchange-rate:{limit}"

    # Try cache first
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    # Fetch and cache
    service = get_macro_service()
    result = await service.get_exchange_rate(limit=limit)
    await cache.set(cache_key, result, CacheTTL.MACRO)
    return result


@router.get("/import-export", response_model=ImportExportResponse)
async def get_import_export(
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
) -> ImportExportResponse:
    """
    Get Vietnam import/export trade data.

    Returns historical trade data including:
    - Report time/period
    - Import values
    - Export values
    - Trade balance
    - By category/country

    **Parameters:**
    - **limit**: Number of records to return (default: 20, max: 100)
    """
    cache = get_cache()
    cache_key = f"macro:import-export:{limit}"

    # Try cache first
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    # Fetch and cache
    service = get_macro_service()
    result = await service.get_import_export(limit=limit)
    await cache.set(cache_key, result, CacheTTL.MACRO)
    return result


@router.get("/fdi", response_model=FDIResponse)
async def get_fdi(
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
) -> FDIResponse:
    """
    Get Vietnam FDI (Foreign Direct Investment) data.

    Returns historical FDI data including:
    - Report time/period
    - Registered capital
    - Disbursed capital
    - By sector/country

    **Parameters:**
    - **limit**: Number of records to return (default: 20, max: 100)
    """
    cache = get_cache()
    cache_key = f"macro:fdi:{limit}"

    # Try cache first
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    # Fetch and cache
    service = get_macro_service()
    result = await service.get_fdi(limit=limit)
    await cache.set(cache_key, result, CacheTTL.MACRO)
    return result


@router.get("/money-supply", response_model=MoneySupplyResponse)
async def get_money_supply(
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
) -> MoneySupplyResponse:
    """
    Get Vietnam money supply M2 data.

    Returns historical money supply data including:
    - Report time/period
    - M2 value
    - Growth rate
    - Components breakdown

    **Parameters:**
    - **limit**: Number of records to return (default: 20, max: 100)
    """
    cache = get_cache()
    cache_key = f"macro:money-supply:{limit}"

    # Try cache first
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    # Fetch and cache
    service = get_macro_service()
    result = await service.get_money_supply(limit=limit)
    await cache.set(cache_key, result, CacheTTL.MACRO)
    return result

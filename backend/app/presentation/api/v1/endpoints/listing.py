"""Listing endpoints with async optimization."""
from typing import Any, Dict

from fastapi import APIRouter, Path

from app.application.listing.dtos import ListingResponse
from app.application.listing.services import ListingService
from app.infrastructure.vnstock.listing_provider import VnstockListingProvider
from app.core.cache import get_cache, CacheTTL
from app.core.async_utils import run_sync

router = APIRouter(prefix="/listing", tags=["Listing"])

# Singleton provider
_listing_provider = None


def _get_provider() -> VnstockListingProvider:
    global _listing_provider
    if _listing_provider is None:
        _listing_provider = VnstockListingProvider()
    return _listing_provider


def get_listing_service() -> ListingService:
    return ListingService(data_provider=_get_provider())


@router.get("/stocks", response_model=ListingResponse)
async def get_stocks() -> ListingResponse:
    """Get all stock symbols."""
    cache = get_cache()
    cache_key = "listing:stocks"
    
    cached = await cache.get(cache_key)
    if cached:
        return cached
        
    service = get_listing_service()
    result = await run_sync(service.get_stocks)
    await cache.set(cache_key, result, CacheTTL.COMMON_INFO)
    return result


@router.get("/etfs", response_model=ListingResponse)
async def get_etfs() -> ListingResponse:
    """Get all ETFs."""
    cache = get_cache()
    cache_key = "listing:etfs"
    
    cached = await cache.get(cache_key)
    if cached:
        return cached
        
    service = get_listing_service()
    result = await run_sync(service.get_etfs)
    await cache.set(cache_key, result, CacheTTL.COMMON_INFO)
    return result


@router.get("/industries", response_model=ListingResponse)
async def get_industries() -> ListingResponse:
    """Get classification of industries."""
    cache = get_cache()
    cache_key = "listing:industries"
    
    cached = await cache.get(cache_key)
    if cached:
        return cached
        
    service = get_listing_service()
    result = await run_sync(service.get_industries)
    await cache.set(cache_key, result, CacheTTL.COMMON_INFO)
    return result


@router.get("/industries/icb", response_model=ListingResponse)
async def get_industries_icb() -> ListingResponse:
    """Get ICB classification."""
    cache = get_cache()
    cache_key = "listing:industries:icb"

    cached = await cache.get(cache_key)
    if cached:
        return cached

    service = get_listing_service()
    result = await run_sync(service.get_industries_icb)
    await cache.set(cache_key, result, CacheTTL.COMMON_INFO)
    return result


@router.get("/groups/{group}")
async def get_symbols_by_group(
    group: str = Path(..., description="Group name: VN30, HNX30, VNMID, VN100, VNALL, etc."),
) -> Dict[str, Any]:
    """Get symbols by index group.

    Available groups:
    - VN30: Top 30 stocks on HOSE by market cap and liquidity
    - HNX30: Top 30 stocks on HNX
    - VNMID: Mid-cap stocks
    - VNSML: Small-cap stocks
    - VN100: Top 100 stocks
    - VNALL: All stocks
    - ETF: All ETFs
    """
    cache = get_cache()
    cache_key = f"listing:group:{group.upper()}"

    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    provider = VnstockListingProvider()
    data = await run_sync(provider.get_symbols_by_group, group=group.upper())
    result = {"group": group.upper(), "data": data, "count": len(data)}
    await cache.set(cache_key, result, CacheTTL.SYMBOL_LIST)
    return result

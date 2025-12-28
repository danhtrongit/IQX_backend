"""Cache management endpoints."""
from fastapi import APIRouter, Query

from app.core.cache import get_cache, CacheTTL
from app.presentation.deps.auth_deps import CurrentUser

router = APIRouter(prefix="/cache", tags=["Cache"])


@router.get("/stats")
async def get_cache_stats():
    """
    Get cache statistics.
    
    Returns:
    - entries: Number of cached entries
    - hits: Number of cache hits
    - misses: Number of cache misses
    - sets: Number of cache sets
    - hit_rate: Cache hit rate percentage
    """
    cache = get_cache()
    return cache.get_stats()


@router.get("/ttl-config")
async def get_ttl_config():
    """
    Get current cache TTL configuration.
    
    Returns the TTL values (in seconds) for different data types.
    """
    return {
        "realtime": CacheTTL.REALTIME,
        "market_overview": CacheTTL.MARKET_OVERVIEW,
        "price_board": CacheTTL.PRICE_BOARD,
        "intraday": CacheTTL.INTRADAY,
        "top_stocks": CacheTTL.TOP_STOCKS,
        "historical_recent": CacheTTL.HISTORICAL_RECENT,
        "historical_old": CacheTTL.HISTORICAL_OLD,
        "company_info": CacheTTL.COMPANY_INFO,
        "financials": CacheTTL.FINANCIALS,
        "symbol_list": CacheTTL.SYMBOL_LIST,
        "industries": CacheTTL.INDUSTRIES,
        "company_overview": CacheTTL.COMPANY_OVERVIEW,
        "officers": CacheTTL.OFFICERS,
    }


@router.delete("/clear")
async def clear_cache(
    current_user: CurrentUser,
    pattern: str = Query(None, description="Optional pattern prefix to clear (e.g., 'market:', 'quotes:')")
):
    """
    Clear cache entries.
    
    Requires authentication.
    
    - **pattern**: Optional prefix to clear specific cache entries.
      If not provided, clears ALL cache entries.
    
    Examples:
    - Clear all: DELETE /api/v1/cache/clear
    - Clear market: DELETE /api/v1/cache/clear?pattern=market:
    - Clear quotes: DELETE /api/v1/cache/clear?pattern=quotes:
    """
    cache = get_cache()
    
    if pattern:
        count = await cache.delete_pattern(pattern)
        return {
            "cleared": True,
            "pattern": pattern,
            "deleted_count": count,
        }
    else:
        await cache.clear()
        return {
            "cleared": True,
            "pattern": "all",
            "message": "All cache entries cleared",
        }


@router.delete("/key/{key}")
async def delete_cache_key(
    key: str,
    current_user: CurrentUser,
):
    """
    Delete a specific cache key.
    
    Requires authentication.
    """
    cache = get_cache()
    deleted = await cache.delete(key)
    return {
        "key": key,
        "deleted": deleted,
    }

"""Symbol endpoints."""
from typing import Optional, List
from fastapi import APIRouter, Query

from app.application.symbol.dtos import (
    SymbolListRequest,
    SymbolSearchRequest,
    SymbolResponse,
    SymbolDetailResponse,
    SymbolListResponse,
    IndustryListResponse,
    SyncResultResponse,
)
from app.application.symbol.services import SymbolService
from app.infrastructure.repositories.symbol_repo import (
    SQLAlchemySymbolRepository,
    SQLAlchemyIndustryRepository,
)
from app.infrastructure.vnstock.provider import VnstockProvider
from app.presentation.deps.auth_deps import CurrentUser, DBSession
from app.core.cache import get_cache, CacheTTL

router = APIRouter(prefix="/symbols", tags=["Symbols"])


def get_symbol_service(db: DBSession) -> SymbolService:
    """Create symbol service with dependencies."""
    return SymbolService(
        symbol_repo=SQLAlchemySymbolRepository(db),
        industry_repo=SQLAlchemyIndustryRepository(db),
    )


@router.get("", response_model=SymbolListResponse)
async def list_symbols(
    db: DBSession,
    exchange: Optional[str] = Query(None, description="Filter by exchange: HOSE, HNX, UPCOM"),
    type: Optional[str] = Query(None, description="Filter by type: STOCK, ETF, CW, BOND"),
    icb_code2: Optional[str] = Query(None, description="Filter by ICB level 2 code"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> SymbolListResponse:
    """List all symbols with optional filters."""
    cache = get_cache()
    cache_key = f"symbols:list:{exchange}:{type}:{icb_code2}:{is_active}:{limit}:{offset}"
    
    # Try cache first
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    # Fetch and cache
    service = get_symbol_service(db)
    request = SymbolListRequest(
        exchange=exchange,
        type=type,
        icb_code2=icb_code2,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )
    result = await service.list_symbols(request)
    await cache.set(cache_key, result, CacheTTL.SYMBOL_LIST)
    return result


@router.get("/search", response_model=List[SymbolResponse])
async def search_symbols(
    db: DBSession,
    q: str = Query(..., min_length=1, max_length=50, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
) -> List[SymbolResponse]:
    """Search symbols by name or code."""
    cache = get_cache()
    cache_key = f"symbols:search:{q}:{limit}"
    
    # Try cache first
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    # Fetch and cache
    service = get_symbol_service(db)
    request = SymbolSearchRequest(query=q, limit=limit)
    result = await service.search_symbols(request)
    await cache.set(cache_key, result, CacheTTL.SYMBOL_LIST)
    return result


@router.get("/industries", response_model=IndustryListResponse)
async def list_industries(
    db: DBSession,
    level: Optional[int] = Query(None, ge=1, le=4, description="Filter by ICB level (1-4)"),
) -> IndustryListResponse:
    """List all ICB industries."""
    cache = get_cache()
    cache_key = f"symbols:industries:{level}"
    
    # Try cache first
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    # Fetch and cache
    service = get_symbol_service(db)
    result = await service.list_industries(level=level)
    await cache.set(cache_key, result, CacheTTL.INDUSTRIES)
    return result


@router.get("/{symbol}", response_model=SymbolDetailResponse)
async def get_symbol(
    symbol: str,
    db: DBSession,
) -> SymbolDetailResponse:
    """Get symbol detail by ticker code."""
    cache = get_cache()
    cache_key = f"symbols:detail:{symbol.upper()}"
    
    # Try cache first
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
    # Fetch and cache
    service = get_symbol_service(db)
    result = await service.get_symbol(symbol)
    await cache.set(cache_key, result, CacheTTL.SYMBOL_LIST)
    return result


@router.post("/sync", response_model=SyncResultResponse)
async def sync_symbols(
    db: DBSession,
    current_user: CurrentUser,
    sync_details: bool = Query(False, description="Also sync company details (slower)"),
) -> SyncResultResponse:
    """
    Sync symbols from vnstock data source.
    Requires authentication.
    """
    # Clear symbol cache after sync
    cache = get_cache()
    await cache.delete_pattern("symbols:")
    
    service = get_symbol_service(db)
    provider = VnstockProvider()
    return await service.sync_from_vnstock(
        data_provider=provider,
        sync_details=sync_details,
    )

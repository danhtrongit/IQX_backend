"""Symbol DTOs."""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field


# === Request DTOs ===

class SymbolListRequest(BaseModel):
    """Symbol list request with filters."""
    
    exchange: Optional[str] = Field(None, description="Filter by exchange: HOSE, HNX, UPCOM")
    type: Optional[str] = Field(None, description="Filter by type: STOCK, ETF, CW, BOND")
    icb_code2: Optional[str] = Field(None, description="Filter by ICB level 2 code")
    is_active: Optional[bool] = Field(True, description="Filter by active status")
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class SymbolSearchRequest(BaseModel):
    """Symbol search request."""
    
    query: str = Field(..., min_length=1, max_length=50)
    limit: int = Field(20, ge=1, le=100)


class SyncSymbolsRequest(BaseModel):
    """Request to sync symbols from vnstock."""
    
    source: str = Field("vci", description="Data source: vci or vnd")
    sync_details: bool = Field(False, description="Also sync company details (slower)")


# === Response DTOs ===

class SymbolResponse(BaseModel):
    """Symbol response."""
    
    id: int
    symbol: str
    organ_name: Optional[str]
    en_organ_name: Optional[str]
    organ_short_name: Optional[str]
    exchange: Optional[str]
    type: Optional[str]
    
    # ICB
    icb_code2: Optional[str]
    icb_code3: Optional[str]
    icb_code4: Optional[str]
    icb_name2: Optional[str]
    icb_name3: Optional[str]
    icb_name4: Optional[str]
    
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SymbolDetailResponse(SymbolResponse):
    """Symbol detail response with company info."""
    
    icb_code1: Optional[str]
    company_profile: Optional[str]
    history: Optional[str]
    issue_share: Optional[Decimal]
    charter_capital: Optional[Decimal]


class SymbolListResponse(BaseModel):
    """Paginated symbol list response."""
    
    items: List[SymbolResponse]
    total: int
    limit: int
    offset: int


class IndustryResponse(BaseModel):
    """Industry response."""
    
    id: int
    icb_code: str
    icb_name: str
    en_icb_name: Optional[str]
    level: int
    parent_code: Optional[str]


class IndustryListResponse(BaseModel):
    """Industry list response."""
    
    items: List[IndustryResponse]
    total: int


class SyncResultResponse(BaseModel):
    """Sync result response."""
    
    synced_count: int
    message: str

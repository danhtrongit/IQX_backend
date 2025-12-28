"""Financial DTOs."""
from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field


# === Request DTOs ===

class FinancialRequest(BaseModel):
    """Financial report request."""
    
    period: str = Field("quarter", description="Period: quarter or year")
    lang: str = Field("vi", description="Language: vi or en")
    limit: int = Field(20, ge=1, le=100, description="Number of periods")


class RatioRequest(BaseModel):
    """Financial ratio request."""
    
    period: str = Field("quarter", description="Period: quarter or year")
    limit: int = Field(20, ge=1, le=100)


# === Response DTOs ===

class FinancialReportResponse(BaseModel):
    """Financial report response."""
    
    symbol: str
    report_type: str  # balance_sheet, income_statement, cash_flow
    period: str
    data: List[Dict[str, Any]]
    count: int


class RatioResponse(BaseModel):
    """Financial ratio response."""
    
    symbol: str
    period: str
    data: List[Dict[str, Any]]
    count: int


# === Company DTOs ===

class CompanyOverviewResponse(BaseModel):
    """Company overview response."""
    
    symbol: str
    company_profile: Optional[str] = None
    history: Optional[str] = None
    icb_name2: Optional[str] = None
    icb_name3: Optional[str] = None
    icb_name4: Optional[str] = None
    issue_share: Optional[float] = None
    charter_capital: Optional[float] = None


class ShareholderItem(BaseModel):
    """Shareholder item."""
    
    share_holder: Optional[str] = None
    share_own_percent: Optional[float] = None
    update_date: Optional[str] = None


class ShareholdersResponse(BaseModel):
    """Shareholders response."""
    
    symbol: str
    data: List[ShareholderItem]


class OfficerItem(BaseModel):
    """Officer item."""
    
    officer_name: Optional[str] = None
    officer_position: Optional[str] = None
    officer_own_percent: Optional[float] = None
    update_date: Optional[str] = None


class OfficersResponse(BaseModel):
    """Officers response."""
    
    symbol: str
    data: List[OfficerItem]


class EventItem(BaseModel):
    """Company event item."""
    
    event_title: Optional[str] = None
    public_date: Optional[str] = None
    issue_date: Optional[str] = None
    event_list_name: Optional[str] = None
    ratio: Optional[float] = None
    value: Optional[float] = None


class EventsResponse(BaseModel):
    """Company events response."""
    
    symbol: str
    data: List[EventItem]


class NewsItem(BaseModel):
    """News item."""
    
    news_title: Optional[str] = None
    news_short_content: Optional[str] = None
    public_date: Optional[str] = None
    news_source_link: Optional[str] = None


class NewsResponse(BaseModel):
    """News response."""
    
    symbol: str
    data: List[NewsItem]


# === Stock Detail DTOs ===

class StockDetailResponse(BaseModel):
    """Stock detail response with trading info for stock detail page."""
    
    symbol: str
    # Price info (from trading_stats)
    match_price: Optional[float] = None
    reference_price: Optional[float] = None
    ceiling_price: Optional[float] = None
    floor_price: Optional[float] = None
    price_change: Optional[float] = None
    percent_price_change: Optional[float] = None
    total_volume: Optional[float] = None
    # 52-week range
    highest_price_1_year: Optional[float] = None
    lowest_price_1_year: Optional[float] = None
    # Foreign ownership
    foreign_total_volume: Optional[float] = None
    foreign_total_room: Optional[float] = None
    foreign_holding_room: Optional[float] = None
    current_holding_ratio: Optional[float] = None  # % foreign ownership
    max_holding_ratio: Optional[float] = None
    # Market cap & shares (from ratio_summary)
    market_cap: Optional[float] = None  # Vốn hóa
    issue_share: Optional[float] = None  # SLCP lưu hành
    charter_capital: Optional[float] = None
    # Financial ratios
    pe: Optional[float] = None
    pb: Optional[float] = None
    eps: Optional[float] = None
    bvps: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    de: Optional[float] = None  # Debt/Equity (Nợ/VCSH)
    # Additional ratios
    ev: Optional[float] = None  # Enterprise value
    dividend: Optional[float] = None


# === Analysis Report DTOs ===

class AnalysisReportItem(BaseModel):
    """Analysis report item from Simplize."""
    
    id: Optional[int] = None
    title: Optional[str] = None
    source: Optional[str] = None  # e.g., "Vietcap", "MAS", "VCSC"
    issue_date: Optional[str] = None  # e.g., "05/09/2025"
    issue_date_ago: Optional[str] = None  # e.g., "3 tháng"
    report_type: Optional[int] = None
    target_price: Optional[float] = None
    recommend: Optional[str] = None  # MUA, BÁN, TRUNG LẬP, KHÁC
    attached_link: Optional[str] = None  # PDF link
    file_name: Optional[str] = None


class AnalysisReportResponse(BaseModel):
    """Analysis report response."""
    
    symbol: str
    data: List[AnalysisReportItem]
    total: int
    page: int
    size: int

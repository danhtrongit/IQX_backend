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


# === Toolkit DTOs ===
# Toolkit spec from toolkit.pdf - 8 charts:
# 1. Cơ cấu tài sản (stacked columns)
# 2. Cơ cấu vốn chủ & nợ phải trả (stacked columns)
# 3. Cơ cấu doanh thu (stacked columns)
# 4. Cơ cấu chi phí (stacked columns)
# 5. HĐKD bridge (CFO waterfall)
# 6. HĐĐT bridge (CFI waterfall)
# 7. HĐTC bridge (CFF waterfall)
# 8. Lưu chuyển tiền tệ thuần (net cash flow)

class ToolkitRequest(BaseModel):
    """Toolkit request."""

    period: str = Field("year", description="Period: quarter or year")
    limit: int = Field(3, ge=1, le=20, description="Number of periods (default 3 years)")
    lang: str = Field("vi", description="Language: vi or en")


class ToolkitSummary(BaseModel):
    """Summary metrics for toolkit - 5 cards as per spec."""

    roe: Optional[float] = None
    roa: Optional[float] = None
    debt_equity: Optional[float] = None
    gross_margin: Optional[float] = None
    net_margin: Optional[float] = None


class ToolkitSeriesItem(BaseModel):
    """Single series item for charts."""

    key: str
    name: str
    values: List[Optional[float]]


class ToolkitPercentSeriesItem(BaseModel):
    """Percent series item for stacked charts."""

    key: str
    values: List[Optional[float]]


class ToolkitComposition(BaseModel):
    """Composition data for stacked bar charts."""

    labels: List[str]
    series: List[ToolkitSeriesItem]
    percent_series: List[ToolkitPercentSeriesItem]


class ToolkitBridgeItem(BaseModel):
    """Single item in a bridge/waterfall chart."""

    key: str
    name: str
    values: List[Optional[float]]
    bridge_type: str = "flow"  # "start", "flow", "end"


class ToolkitBridgeChart(BaseModel):
    """Bridge/waterfall chart data for cash flow analysis."""

    labels: List[str]
    items: List[ToolkitBridgeItem]


class ToolkitNetCashFlow(BaseModel):
    """Net cash flow (delta_cash = cfo + cfi + cff)."""

    labels: List[str]
    cfo: List[Optional[float]]
    cfi: List[Optional[float]]
    cff: List[Optional[float]]
    delta_cash: List[Optional[float]]


class ToolkitCompareItem(BaseModel):
    """Single item for single-period comparison view."""

    key: str
    name: str
    value: Optional[float] = None
    percent_of_total: Optional[float] = None


class ToolkitSinglePeriodCompare(BaseModel):
    """Comparison bars for a single period (latest in requested range)."""

    period_label: str
    total_key: str
    total_name: str
    total_value: Optional[float] = None
    items: List[ToolkitCompareItem]


class ToolkitResponse(BaseModel):
    """Toolkit response with aggregated financial data - 8 charts as per toolkit.pdf."""

    symbol: str
    type: str  # "bank" or "non-bank"
    period: str
    limit: int
    summary: ToolkitSummary
    # Chart 1: Cơ cấu tài sản (Bank vs Non-Bank variants)
    asset_composition: ToolkitComposition
    # Chart 2: Cơ cấu vốn chủ & nợ phải trả
    liability_equity: ToolkitComposition
    # Chart 3: Cơ cấu doanh thu (gross_profit, financial_income, other_income)
    revenue_composition: ToolkitComposition
    # Chart 4: Cơ cấu chi phí (cogs, selling, admin, interest)
    expense_composition: ToolkitComposition
    # Chart 5: HĐKD bridge (CFO waterfall)
    cfo_bridge: ToolkitBridgeChart
    # Chart 6: HĐĐT bridge (CFI waterfall)
    cfi_bridge: ToolkitBridgeChart
    # Chart 7: HĐTC bridge (CFF waterfall)
    cff_bridge: ToolkitBridgeChart
    # Chart 8: Lưu chuyển tiền tệ thuần
    net_cash_flow: ToolkitNetCashFlow

    # Optional: Single-period comparison (when limit=1)
    asset_compare: Optional[ToolkitSinglePeriodCompare] = None
    liability_compare: Optional[ToolkitSinglePeriodCompare] = None
    revenue_compare: Optional[ToolkitSinglePeriodCompare] = None
    expense_compare: Optional[ToolkitSinglePeriodCompare] = None
    cfo_compare: Optional[ToolkitSinglePeriodCompare] = None
    cfi_compare: Optional[ToolkitSinglePeriodCompare] = None
    cff_compare: Optional[ToolkitSinglePeriodCompare] = None
    net_cash_compare: Optional[ToolkitSinglePeriodCompare] = None

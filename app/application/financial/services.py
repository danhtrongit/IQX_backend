"""Financial application services."""
from typing import Optional, List, Protocol, Dict, Any

from app.application.financial.dtos import (
    FinancialRequest,
    RatioRequest,
    FinancialReportResponse,
    RatioResponse,
    CompanyOverviewResponse,
    ShareholderItem,
    ShareholdersResponse,
    OfficerItem,
    OfficersResponse,
    EventItem,
    EventsResponse,
    NewsItem,
    NewsResponse,
    StockDetailResponse,
    AnalysisReportItem,
    AnalysisReportResponse,
)


class FinancialDataProvider(Protocol):
    """Financial data provider interface."""
    
    def get_balance_sheet(
        self, symbol: str, period: str, lang: str, limit: int
    ) -> List[Dict[str, Any]]:
        ...
    
    def get_income_statement(
        self, symbol: str, period: str, lang: str, limit: int
    ) -> List[Dict[str, Any]]:
        ...
    
    def get_cash_flow(
        self, symbol: str, period: str, lang: str, limit: int
    ) -> List[Dict[str, Any]]:
        ...
    
    def get_ratio(
        self, symbol: str, period: str, limit: int
    ) -> List[Dict[str, Any]]:
        ...


class CompanyDataProvider(Protocol):
    """Company data provider interface."""
    
    def get_overview(self, symbol: str) -> Optional[Dict[str, Any]]:
        ...
    
    def get_shareholders(self, symbol: str) -> List[Dict[str, Any]]:
        ...
    
    def get_officers(self, symbol: str, filter_by: str) -> List[Dict[str, Any]]:
        ...
    
    def get_events(self, symbol: str) -> List[Dict[str, Any]]:
        ...
    
    def get_news(self, symbol: str) -> List[Dict[str, Any]]:
        ...
    
    def get_trading_stats(self, symbol: str) -> Optional[Dict[str, Any]]:
        ...
    
    def get_ratio_summary(self, symbol: str) -> Optional[Dict[str, Any]]:
        ...
    
    def get_analysis_reports(
        self, symbol: str, page: int, size: int
    ) -> Dict[str, Any]:
        """Get analysis reports from Simplize."""
        ...


class FinancialService:
    """Financial service."""
    
    def __init__(self, data_provider: FinancialDataProvider):
        self.data_provider = data_provider
    
    def get_balance_sheet(
        self, symbol: str, request: FinancialRequest
    ) -> FinancialReportResponse:
        """Get balance sheet."""
        data = self.data_provider.get_balance_sheet(
            symbol=symbol.upper(),
            period=request.period,
            lang=request.lang,
            limit=request.limit,
        )
        return FinancialReportResponse(
            symbol=symbol.upper(),
            report_type="balance_sheet",
            period=request.period,
            data=data,
            count=len(data),
        )
    
    def get_income_statement(
        self, symbol: str, request: FinancialRequest
    ) -> FinancialReportResponse:
        """Get income statement."""
        data = self.data_provider.get_income_statement(
            symbol=symbol.upper(),
            period=request.period,
            lang=request.lang,
            limit=request.limit,
        )
        return FinancialReportResponse(
            symbol=symbol.upper(),
            report_type="income_statement",
            period=request.period,
            data=data,
            count=len(data),
        )
    
    def get_cash_flow(
        self, symbol: str, request: FinancialRequest
    ) -> FinancialReportResponse:
        """Get cash flow statement."""
        data = self.data_provider.get_cash_flow(
            symbol=symbol.upper(),
            period=request.period,
            lang=request.lang,
            limit=request.limit,
        )
        return FinancialReportResponse(
            symbol=symbol.upper(),
            report_type="cash_flow",
            period=request.period,
            data=data,
            count=len(data),
        )
    
    def get_ratio(self, symbol: str, request: RatioRequest) -> RatioResponse:
        """Get financial ratios."""
        data = self.data_provider.get_ratio(
            symbol=symbol.upper(),
            period=request.period,
            limit=request.limit,
        )
        return RatioResponse(
            symbol=symbol.upper(),
            period=request.period,
            data=data,
            count=len(data),
        )


class CompanyService:
    """Company service."""
    
    def __init__(self, data_provider: CompanyDataProvider):
        self.data_provider = data_provider
    
    def get_overview(self, symbol: str) -> CompanyOverviewResponse:
        """Get company overview."""
        data = self.data_provider.get_overview(symbol.upper())
        if not data:
            data = {}
        return CompanyOverviewResponse(
            symbol=symbol.upper(),
            company_profile=data.get("company_profile"),
            history=data.get("history"),
            icb_name2=data.get("icb_name2"),
            icb_name3=data.get("icb_name3"),
            icb_name4=data.get("icb_name4"),
            issue_share=self._safe_float(data.get("issue_share")),
            charter_capital=self._safe_float(data.get("charter_capital")),
        )
    
    def get_shareholders(self, symbol: str) -> ShareholdersResponse:
        """Get shareholders."""
        data = self.data_provider.get_shareholders(symbol.upper())
        items = [
            ShareholderItem(
                share_holder=row.get("share_holder"),
                share_own_percent=self._safe_float(row.get("share_own_percent")),
                update_date=self._safe_str(row.get("update_date")),
            )
            for row in data
        ]
        return ShareholdersResponse(symbol=symbol.upper(), data=items)
    
    def get_officers(self, symbol: str, filter_by: str = "working") -> OfficersResponse:
        """Get officers."""
        data = self.data_provider.get_officers(symbol.upper(), filter_by)
        items = [
            OfficerItem(
                officer_name=row.get("officer_name"),
                officer_position=row.get("officer_position"),
                officer_own_percent=self._safe_float(row.get("officer_own_percent")),
                update_date=self._safe_str(row.get("update_date")),
            )
            for row in data
        ]
        return OfficersResponse(symbol=symbol.upper(), data=items)
    
    def get_events(self, symbol: str) -> EventsResponse:
        """Get company events."""
        data = self.data_provider.get_events(symbol.upper())
        items = [
            EventItem(
                event_title=row.get("event_title"),
                public_date=self._safe_str(row.get("public_date")),
                issue_date=self._safe_str(row.get("issue_date")),
                event_list_name=row.get("event_list_name"),
                ratio=self._safe_float(row.get("ratio")),
                value=self._safe_float(row.get("value")),
            )
            for row in data
        ]
        return EventsResponse(symbol=symbol.upper(), data=items)
    
    def get_news(self, symbol: str) -> NewsResponse:
        """Get company news."""
        data = self.data_provider.get_news(symbol.upper())
        items = [
            NewsItem(
                news_title=row.get("news_title"),
                news_short_content=row.get("news_short_content"),
                public_date=self._safe_str(row.get("public_date")),
                news_source_link=row.get("news_source_link"),
            )
            for row in data
        ]
        return NewsResponse(symbol=symbol.upper(), data=items)
    
    @staticmethod
    def _safe_float(value) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _safe_str(value) -> Optional[str]:
        """Convert value to string, handling timestamps."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            # Timestamp in milliseconds - convert to ISO format
            from datetime import datetime
            try:
                ts = value / 1000 if value > 1e12 else value
                return datetime.fromtimestamp(ts).isoformat()
            except (ValueError, OSError):
                return str(value)
        return str(value)
    
    def get_stock_detail(self, symbol: str) -> StockDetailResponse:
        """
        Get stock detail for stock detail page.
        
        Combines trading stats (price, foreign ownership) and ratio summary
        (market cap, PE, PB, EPS, etc.)
        """
        symbol = symbol.upper()
        
        # Get trading stats (price info, foreign ownership)
        trading_stats = self.data_provider.get_trading_stats(symbol) or {}
        
        # Get ratio summary (market cap, PE, PB, etc.)
        ratio_summary = self.data_provider.get_ratio_summary(symbol) or {}
        
        # Calculate market cap: match_price * issue_share
        match_price = self._safe_float(trading_stats.get("match_price"))
        issue_share = self._safe_float(ratio_summary.get("issue_share"))
        market_cap = None
        if match_price and issue_share:
            market_cap = match_price * issue_share
        
        return StockDetailResponse(
            symbol=symbol,
            # Price info from trading_stats
            match_price=match_price,
            reference_price=self._safe_float(trading_stats.get("ref_price")),
            ceiling_price=self._safe_float(trading_stats.get("ceiling")),
            floor_price=self._safe_float(trading_stats.get("floor")),
            price_change=self._safe_float(trading_stats.get("price_change")),
            percent_price_change=self._safe_float(trading_stats.get("price_change_pct")),
            total_volume=self._safe_float(trading_stats.get("total_volume")),
            # 52-week range
            highest_price_1_year=self._safe_float(trading_stats.get("high_price_1y")),
            lowest_price_1_year=self._safe_float(trading_stats.get("low_price_1y")),
            # Foreign ownership
            foreign_total_volume=self._safe_float(trading_stats.get("foreign_volume")),
            foreign_total_room=self._safe_float(trading_stats.get("foreign_room")),
            foreign_holding_room=self._safe_float(trading_stats.get("foreign_holding_room")),
            current_holding_ratio=self._safe_float(trading_stats.get("current_holding_ratio")),
            max_holding_ratio=self._safe_float(trading_stats.get("max_holding_ratio")),
            # Market cap & shares
            market_cap=market_cap,
            issue_share=issue_share,
            charter_capital=self._safe_float(ratio_summary.get("charter_capital")),
            # Financial ratios
            pe=self._safe_float(ratio_summary.get("pe")),
            pb=self._safe_float(ratio_summary.get("pb")),
            eps=self._safe_float(ratio_summary.get("eps")),
            bvps=self._safe_float(ratio_summary.get("bvps")),
            roe=self._safe_float(ratio_summary.get("roe")),
            roa=self._safe_float(ratio_summary.get("roa")),
            de=self._safe_float(ratio_summary.get("de")),  # Debt/Equity
            # Additional
            ev=self._safe_float(trading_stats.get("ev")),
            dividend=self._safe_float(ratio_summary.get("dividend")),
        )
    
    def get_analysis_reports(
        self, symbol: str, page: int = 0, size: int = 20
    ) -> AnalysisReportResponse:
        """
        Get analysis reports for a symbol from Simplize.
        
        Args:
            symbol: Stock ticker
            page: Page number (0-indexed)
            size: Number of items per page
        """
        result = self.data_provider.get_analysis_reports(
            symbol=symbol.upper(),
            page=page,
            size=size,
        )
        
        data = result.get("data", [])
        items = [
            AnalysisReportItem(
                id=row.get("id"),
                title=row.get("title"),
                source=row.get("source"),
                issue_date=row.get("issueDate"),
                issue_date_ago=row.get("issueDateTimeAgo"),
                report_type=row.get("reportType"),
                target_price=self._safe_float(row.get("targetPrice")),
                recommend=row.get("recommend"),
                attached_link=row.get("attachedLink"),
                file_name=row.get("fileName"),
            )
            for row in data
        ]
        
        return AnalysisReportResponse(
            symbol=symbol.upper(),
            data=items,
            total=result.get("total", len(items)),
            page=page,
            size=size,
        )

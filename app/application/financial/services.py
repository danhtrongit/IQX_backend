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
    ToolkitRequest,
    ToolkitResponse,
    ToolkitSummary,
    ToolkitSeriesItem,
    ToolkitPercentSeriesItem,
    ToolkitComposition,
    ToolkitComparisonMetric,
    ToolkitComparison,
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

    def get_toolkit(self, symbol: str, request: ToolkitRequest) -> ToolkitResponse:
        """Get toolkit data with aggregated financial metrics."""
        symbol = symbol.upper()

        # Fetch raw data
        balance_data = self.data_provider.get_balance_sheet(
            symbol=symbol,
            period=request.period,
            lang=request.lang,
            limit=request.limit,
        )
        income_data = self.data_provider.get_income_statement(
            symbol=symbol,
            period=request.period,
            lang=request.lang,
            limit=request.limit,
        )
        ratio_data = self.data_provider.get_ratio(
            symbol=symbol,
            period=request.period,
            limit=request.limit,
        )

        # Determine company type (bank vs non-bank)
        # For now, default to non-bank. TODO: detect from ICB classification
        company_type = "non-bank"

        # Build labels from data periods (reverse for chronological order)
        labels = self._build_period_labels(balance_data, request.period)

        # Build summary from latest ratio data
        summary = self._build_summary(ratio_data)

        # Build asset composition
        asset_composition = self._build_asset_composition(balance_data, labels)

        # Build revenue composition
        revenue_composition = self._build_revenue_composition(income_data, labels)

        # Build comparison data with YoY/QoQ
        comparison = self._build_comparison(balance_data, income_data, labels, request.period)

        return ToolkitResponse(
            symbol=symbol,
            type=company_type,
            period=request.period,
            limit=request.limit,
            summary=summary,
            asset_composition=asset_composition,
            revenue_composition=revenue_composition,
            comparison=comparison,
        )

    def _build_period_labels(self, data: List[Dict], period: str) -> List[str]:
        """Build period labels from data, reversed for chronological order."""
        labels = []
        for item in reversed(data):
            year = item.get("Năm") or item.get("Meta_yearReport")
            quarter = item.get("Kỳ") or item.get("Meta_lengthReport")
            if period == "year":
                labels.append(str(year) if year else "—")
            else:
                if year and quarter:
                    labels.append(f"Q{quarter}/{year}")
                else:
                    labels.append("—")
        return labels

    def _build_summary(self, ratio_data: List[Dict]) -> ToolkitSummary:
        """Build summary metrics from latest ratio data."""
        if not ratio_data:
            return ToolkitSummary()

        # Get latest period (first item in list, which is most recent)
        latest = ratio_data[0]

        def get_ratio(key: str) -> Optional[float]:
            val = latest.get(key)
            if val is None:
                return None
            try:
                return float(val)
            except (ValueError, TypeError):
                return None

        return ToolkitSummary(
            roe=get_ratio("Chỉ tiêu khả năng sinh lợi_ROE (%)"),
            roa=get_ratio("Chỉ tiêu khả năng sinh lợi_ROA (%)"),
            debt_equity=get_ratio("Chỉ tiêu cơ cấu nguồn vốn_Debt/Equity"),
            gross_margin=get_ratio("Chỉ tiêu khả năng sinh lợi_Gross Profit Margin (%)"),
            net_margin=get_ratio("Chỉ tiêu khả năng sinh lợi_Net Profit Margin (%)"),
            asset_turnover=get_ratio("Chỉ tiêu hiệu quả hoạt động_Asset Turnover"),
        )

    def _build_asset_composition(
        self, balance_data: List[Dict], labels: List[str]
    ) -> ToolkitComposition:
        """Build asset composition data for stacked bar chart."""
        # Field mappings for non-bank companies
        field_map = {
            "cash_short_invest": [
                "Tiền và tương đương tiền (đồng)",
                "Giá trị thuần đầu tư ngắn hạn (đồng)",
            ],
            "receivable": ["Các khoản phải thu ngắn hạn (đồng)"],
            "inventory": ["Hàng tồn kho, ròng (đồng)"],
            "long_term_invest": ["Đầu tư dài hạn (đồng)"],
            "total_asset": ["TỔNG CỘNG TÀI SẢN (đồng)"],
        }

        name_map = {
            "cash_short_invest": "Tiền & ĐT ngắn hạn",
            "receivable": "Khoản phải thu",
            "inventory": "Hàng tồn kho",
            "long_term_invest": "Đầu tư dài hạn",
            "other_asset": "Tài sản khác",
            "total_asset": "Tổng tài sản",
        }

        # Reverse data for chronological order
        reversed_data = list(reversed(balance_data))

        # Extract values for each component
        series_data: Dict[str, List[Optional[float]]] = {
            key: [] for key in field_map
        }
        series_data["other_asset"] = []

        for item in reversed_data:
            # Sum multiple fields for composite keys
            for key, fields in field_map.items():
                total = 0.0
                has_value = False
                for field in fields:
                    val = item.get(field)
                    if val is not None:
                        try:
                            total += float(val)
                            has_value = True
                        except (ValueError, TypeError):
                            pass
                series_data[key].append(total if has_value else None)

            # Calculate other_asset = total - (known components)
            total_asset = series_data["total_asset"][-1]
            if total_asset is not None:
                known_sum = sum(
                    v or 0
                    for k, v in [
                        ("cash_short_invest", series_data["cash_short_invest"][-1]),
                        ("receivable", series_data["receivable"][-1]),
                        ("inventory", series_data["inventory"][-1]),
                        ("long_term_invest", series_data["long_term_invest"][-1]),
                    ]
                )
                series_data["other_asset"].append(total_asset - known_sum)
            else:
                series_data["other_asset"].append(None)

        # Build series
        series_keys = [
            "cash_short_invest",
            "receivable",
            "inventory",
            "long_term_invest",
            "other_asset",
            "total_asset",
        ]
        series = [
            ToolkitSeriesItem(key=key, name=name_map[key], values=series_data[key])
            for key in series_keys
        ]

        # Build percent series (excluding total_asset)
        percent_keys = [k for k in series_keys if k != "total_asset"]
        percent_series = []
        for key in percent_keys:
            pct_values = []
            for i, val in enumerate(series_data[key]):
                total = series_data["total_asset"][i]
                if val is not None and total and total != 0:
                    pct_values.append(val / total)
                else:
                    pct_values.append(None)
            percent_series.append(ToolkitPercentSeriesItem(key=key, values=pct_values))

        return ToolkitComposition(
            labels=labels,
            series=series,
            percent_series=percent_series,
        )

    def _build_revenue_composition(
        self, income_data: List[Dict], labels: List[str]
    ) -> ToolkitComposition:
        """Build revenue composition data for stacked bar chart."""
        field_map = {
            "core_revenue": ["Doanh thu thuần"],
            "financial_income": ["Thu nhập tài chính"],
            "other_income": ["Thu nhập khác"],
        }

        name_map = {
            "core_revenue": "Doanh thu thuần HĐKD",
            "financial_income": "Doanh thu tài chính",
            "other_income": "Thu nhập khác",
        }

        reversed_data = list(reversed(income_data))

        series_data: Dict[str, List[Optional[float]]] = {key: [] for key in field_map}

        for item in reversed_data:
            for key, fields in field_map.items():
                total = 0.0
                has_value = False
                for field in fields:
                    val = item.get(field)
                    if val is not None:
                        try:
                            total += float(val)
                            has_value = True
                        except (ValueError, TypeError):
                            pass
                series_data[key].append(total if has_value else None)

        series_keys = ["core_revenue", "financial_income", "other_income"]
        series = [
            ToolkitSeriesItem(key=key, name=name_map[key], values=series_data[key])
            for key in series_keys
        ]

        # Calculate total for percent
        totals = []
        for i in range(len(labels)):
            t = sum(
                series_data[k][i] or 0
                for k in series_keys
                if i < len(series_data[k]) and series_data[k][i] is not None
            )
            totals.append(t if t > 0 else None)

        percent_series = []
        for key in series_keys:
            pct_values = []
            for i, val in enumerate(series_data[key]):
                total = totals[i] if i < len(totals) else None
                if val is not None and total and total != 0:
                    pct_values.append(val / total)
                else:
                    pct_values.append(None)
            percent_series.append(ToolkitPercentSeriesItem(key=key, values=pct_values))

        return ToolkitComposition(
            labels=labels,
            series=series,
            percent_series=percent_series,
        )

    def _build_comparison(
        self,
        balance_data: List[Dict],
        income_data: List[Dict],
        labels: List[str],
        period: str,
    ) -> ToolkitComparison:
        """Build comparison data with YoY/QoQ changes."""
        reversed_balance = list(reversed(balance_data))
        reversed_income = list(reversed(income_data))

        def extract_values(data: List[Dict], field: str) -> List[Optional[float]]:
            values = []
            for item in data:
                val = item.get(field)
                if val is not None:
                    try:
                        values.append(float(val))
                    except (ValueError, TypeError):
                        values.append(None)
                else:
                    values.append(None)
            return values

        def calc_yoy(values: List[Optional[float]]) -> List[Optional[float]]:
            """Calculate YoY/QoQ growth rate."""
            yoy = [None]  # First period has no comparison
            for i in range(1, len(values)):
                curr = values[i]
                prev = values[i - 1]
                if curr is not None and prev is not None and prev != 0:
                    yoy.append((curr - prev) / abs(prev))
                else:
                    yoy.append(None)
            return yoy

        # Extract metrics
        total_asset_vals = extract_values(reversed_balance, "TỔNG CỘNG TÀI SẢN (đồng)")
        revenue_vals = extract_values(reversed_income, "Doanh thu thuần")
        net_profit_vals = extract_values(reversed_income, "Lợi nhuận thuần")

        metrics = [
            ToolkitComparisonMetric(
                key="total_asset",
                name="Tổng tài sản",
                values=total_asset_vals,
                yoy=calc_yoy(total_asset_vals),
            ),
            ToolkitComparisonMetric(
                key="core_revenue",
                name="Doanh thu thuần",
                values=revenue_vals,
                yoy=calc_yoy(revenue_vals),
            ),
            ToolkitComparisonMetric(
                key="net_profit",
                name="LN sau thuế",
                values=net_profit_vals,
                yoy=calc_yoy(net_profit_vals),
            ),
        ]

        return ToolkitComparison(labels=labels, metrics=metrics)


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

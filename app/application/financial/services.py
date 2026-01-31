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
    ToolkitBridgeItem,
    ToolkitBridgeChart,
    ToolkitNetCashFlow,
    ToolkitSinglePeriodCompare,
    ToolkitCompareItem,
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
        """Get toolkit data with 8 charts as per toolkit.pdf spec."""
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
        cash_flow_data = self.data_provider.get_cash_flow(
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
        company_type = self._detect_company_type(balance_data)

        # Build labels from data periods (reverse for chronological order)
        labels = self._build_period_labels(balance_data, request.period)

        # Build summary (5 cards)
        summary = self._build_summary(ratio_data)

        # Chart 1: Cơ cấu tài sản (Bank vs Non-Bank variants)
        asset_composition = self._build_asset_composition(balance_data, labels, company_type)

        asset_compare = None
        liability_compare = None
        revenue_compare = None
        expense_compare = None
        cfo_compare = None
        cfi_compare = None
        cff_compare = None
        net_cash_compare = None
        if request.limit == 1 and labels:
            # latest (only) period in chronological labels
            period_label = labels[-1]
            # Build value map from the computed composition
            value_map = {s.key: (s.values[-1] if s.values else None) for s in asset_composition.series}
            total_value = None
            # total asset exists in internal series_data, but not exposed in series. Recompute from balance_data[0].
            # Since limit==1, balance_data[0] corresponds to latest period in provider order; labels is built from balance_data.
            latest_item = balance_data[0] if balance_data else {}
            total_value = self._get_sum(latest_item, ["TỔNG CỘNG TÀI SẢN (đồng)"])
            if total_value is None:
                total_value = value_map.get("cash_short_invest", 0)
                for k in ("receivable","inventory","long_term_invest","other_asset"):
                    total_value = (total_value or 0) + (value_map.get(k) or 0)

            asset_compare = self._build_single_period_compare(
                period_label=period_label,
                total_key="total_asset",
                total_name="Tổng tài sản",
                total_value=total_value,
                keys=[s.key for s in asset_composition.series] + ["total_asset"],
                name_map={s.key: s.name for s in asset_composition.series} | {"total_asset": "Tổng tài sản"},
                values_map=value_map | {"total_asset": total_value},
            )


        # Chart 2: Cơ cấu vốn chủ & nợ phải trả
        liability_equity = self._build_liability_equity(balance_data, labels)

        # Chart 3: Cơ cấu doanh thu (gross_profit, financial_income, other_income)
        revenue_composition = self._build_revenue_composition_v2(income_data, labels)

        # Chart 4: Cơ cấu chi phí (cogs, selling, admin, interest)
        expense_composition = self._build_expense_composition(income_data, labels)

        # Chart 5: HĐKD bridge (CFO waterfall)
        cfo_bridge = self._build_cfo_bridge(cash_flow_data, labels)

        # Chart 6: HĐĐT bridge (CFI waterfall)
        cfi_bridge = self._build_cfi_bridge(cash_flow_data, labels)

        # Chart 7: HĐTC bridge (CFF waterfall)
        cff_bridge = self._build_cff_bridge(cash_flow_data, labels)

        # Chart 8: Lưu chuyển tiền tệ thuần
        net_cash_flow = self._build_net_cash_flow(cash_flow_data, labels)

        # Single-period compares (for 1 kỳ view: multiple bars)
        if request.limit == 1 and labels:
            period_label = labels[-1]

            latest_balance = balance_data[0] if balance_data else {}
            latest_income = income_data[0] if income_data else {}
            latest_cf = cash_flow_data[0] if cash_flow_data else {}

            # Chart 1 compare (asset)
            value_map = {s.key: (s.values[-1] if s.values else None) for s in asset_composition.series}
            total_value = self._get_sum(latest_balance, ["TỔNG CỘNG TÀI SẢN (đồng)"])
            if total_value is None:
                total_value = sum((value_map.get(k) or 0) for k in value_map.keys())
                if total_value == 0:
                    total_value = None
            asset_compare = self._build_single_period_compare(
                period_label=period_label,
                total_key="total_asset",
                total_name="Tổng tài sản",
                total_value=total_value,
                keys=[s.key for s in asset_composition.series] + ["total_asset"],
                name_map={s.key: s.name for s in asset_composition.series} | {"total_asset": "Tổng tài sản"},
                values_map=value_map | {"total_asset": total_value},
            )

            # Chart 2 compare
            total_sources = self._get_sum(latest_balance, ["TỔNG CỘNG NGUỒN VỐN (đồng)"])
            liability_compare = self._build_compare_from_composition(
                period_label=period_label,
                comp=liability_equity,
                total_key="total_sources",
                total_name="Tổng nguồn vốn",
                total_value=total_sources,
            )

            # Chart 3 compare
            revenue_total = None
            if revenue_composition.series:
                revenue_total = sum((s.values[-1] or 0) for s in revenue_composition.series if s.values and s.values[-1] is not None)
                if revenue_total == 0:
                    revenue_total = None
            revenue_compare = self._build_compare_from_composition(
                period_label=period_label,
                comp=revenue_composition,
                total_key="total",
                total_name="Tổng",
                total_value=revenue_total,
            )

            # Chart 4 compare
            expense_total = None
            if expense_composition.series:
                expense_total = sum((s.values[-1] or 0) for s in expense_composition.series if s.values and s.values[-1] is not None)
                if expense_total == 0:
                    expense_total = None
            expense_compare = self._build_compare_from_composition(
                period_label=period_label,
                comp=expense_composition,
                total_key="total",
                total_name="Tổng",
                total_value=expense_total,
            )

            # Bridge compares (5-7)
            cfo_compare = self._build_compare_from_bridge(period_label=period_label, bridge=cfo_bridge, total_key="cfo", total_name="CFO")
            cfi_compare = self._build_compare_from_bridge(period_label=period_label, bridge=cfi_bridge, total_key="cfi", total_name="CFI")
            cff_compare = self._build_compare_from_bridge(period_label=period_label, bridge=cff_bridge, total_key="cff", total_name="CFF")

            # Net cash compare (8)
            net_cash_compare = self._build_compare_from_net_cash_flow(period_label=period_label, net=net_cash_flow)

        return ToolkitResponse(
            symbol=symbol,
            type=company_type,
            period=request.period,
            limit=request.limit,
            summary=summary,
            asset_composition=asset_composition,
            asset_compare=asset_compare,
            liability_compare=liability_compare,
            revenue_compare=revenue_compare,
            expense_compare=expense_compare,
            cfo_compare=cfo_compare,
            cfi_compare=cfi_compare,
            cff_compare=cff_compare,
            net_cash_compare=net_cash_compare,
            liability_equity=liability_equity,
            revenue_composition=revenue_composition,
            expense_composition=expense_composition,
            cfo_bridge=cfo_bridge,
            cfi_bridge=cfi_bridge,
            cff_bridge=cff_bridge,
            net_cash_flow=net_cash_flow,
        )

    def _detect_company_type(self, balance_data: List[Dict]) -> str:
        """Detect if company is a bank or non-bank based on balance sheet fields."""
        if not balance_data:
            return "non-bank"
        sample = balance_data[0]
        # Bank-specific fields
        bank_fields = [
            "Tiền gửi tại NHNN (đồng)",
            "Tiền gửi và cho vay tại các TCTD khác (đồng)",
            "Cho vay khách hàng (đồng)",
        ]
        for field in bank_fields:
            if sample.get(field) is not None:
                return "bank"
        return "non-bank"

    def _get_value_with_fallback(self, item: Dict, candidates: List[str]) -> Optional[float]:
        """Get numeric value using first matching key from candidates.

        Handles common vnstock/vci variations like presence/absence of '(đồng)'.
        """
        for key in candidates:
            for k in (key, key.replace('(đồng)', '').strip() if '(đồng)' in key else None):
                if not k:
                    continue
                val = item.get(k)
                if val is None or val == '':
                    continue
                try:
                    return float(val)
                except (ValueError, TypeError):
                    continue
        return None

    def _build_period_labels(self, data: List[Dict], period: str) -> List[str]:
        """Build period labels from data, reversed for chronological order.

        vnstock/vci sometimes returns different meta field names depending on period/lang.
        We try a few common variants to avoid empty labels (which causes charts 2-8 to show empty).
        """

        def pick(d: Dict, keys: list[str]):
            for k in keys:
                v = d.get(k)
                if v is not None and v != "":
                    return v
            return None

        year_keys = ["Năm", "Meta_yearReport", "yearReport", "Year", "year"]
        quarter_keys = ["Kỳ", "Meta_lengthReport", "lengthReport", "Quarter", "quarter"]

        labels: List[str] = []
        for item in reversed(data):
            year = pick(item, year_keys)
            quarter = pick(item, quarter_keys)

            if period == "year":
                labels.append(str(year) if year is not None else "—")
            else:
                if year is not None and quarter is not None:
                    labels.append(f"Q{quarter}/{year}")
                else:
                    # Fallback: still show year if present to avoid blank axis
                    labels.append(str(year) if year is not None else "—")

        return labels

    def _build_summary(self, ratio_data: List[Dict]) -> ToolkitSummary:
        """Build 5 summary metrics from latest ratio data."""
        if not ratio_data:
            return ToolkitSummary()

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
        )

    def _build_single_period_compare(
        self,
        *,
        period_label: str,
        total_key: str,
        total_name: str,
        total_value: float | None,
        keys: list[str],
        name_map: dict[str, str],
        values_map: dict[str, float | None],
    ) -> ToolkitSinglePeriodCompare:
        items = []
        for k in keys:
            v = values_map.get(k)
            pct = None
            if total_value not in (None, 0) and v is not None:
                pct = v / total_value
            items.append(ToolkitCompareItem(key=k, name=name_map.get(k, k), value=v, percent_of_total=pct))

        return ToolkitSinglePeriodCompare(
            period_label=period_label,
            total_key=total_key,
            total_name=total_name,
            total_value=total_value,
            items=items,
        )

    def _build_compare_from_composition(
        self,
        *,
        period_label: str,
        comp: "ToolkitComposition",
        total_key: str,
        total_name: str,
        total_value: float | None,
    ) -> ToolkitSinglePeriodCompare:
        value_map = {s.key: (s.values[-1] if s.values else None) for s in comp.series}
        name_map = {s.key: s.name for s in comp.series}
        keys = [s.key for s in comp.series] + [total_key]
        value_map[total_key] = total_value
        name_map[total_key] = total_name
        return self._build_single_period_compare(
            period_label=period_label,
            total_key=total_key,
            total_name=total_name,
            total_value=total_value,
            keys=keys,
            name_map=name_map,
            values_map=value_map,
        )


    def _build_compare_from_bridge(
        self,
        *,
        period_label: str,
        bridge: "ToolkitBridgeChart",
        total_key: str,
        total_name: str,
    ) -> ToolkitSinglePeriodCompare:
        # For bridges, percent_of_total is typically not meaningful (can be negative).
        items = []
        total_value = None
        for it in bridge.items:
            v = it.values[-1] if it.values else None
            if it.bridge_type == "end":
                total_value = v
            items.append(ToolkitCompareItem(key=it.key, name=it.name, value=v, percent_of_total=None))
        # Ensure total exists
        if not any(i.key == total_key for i in items):
            items.append(ToolkitCompareItem(key=total_key, name=total_name, value=total_value, percent_of_total=None))
        return ToolkitSinglePeriodCompare(
            period_label=period_label,
            total_key=total_key,
            total_name=total_name,
            total_value=total_value,
            items=items,
        )


    def _build_compare_from_net_cash_flow(
        self,
        *,
        period_label: str,
        net: "ToolkitNetCashFlow",
    ) -> ToolkitSinglePeriodCompare:
        def last(arr):
            return arr[-1] if arr else None
        items = [
            ToolkitCompareItem(key="cfo", name="HĐKD", value=last(net.cfo), percent_of_total=None),
            ToolkitCompareItem(key="cfi", name="HĐĐT", value=last(net.cfi), percent_of_total=None),
            ToolkitCompareItem(key="cff", name="HĐTC", value=last(net.cff), percent_of_total=None),
            ToolkitCompareItem(key="delta_cash", name="Thuần", value=last(net.delta_cash), percent_of_total=None),
        ]
        total_value = last(net.delta_cash)
        return ToolkitSinglePeriodCompare(
            period_label=period_label,
            total_key="delta_cash",
            total_name="Thuần",
            total_value=total_value,
            items=items,
        )

    def _build_asset_composition(
        self, balance_data: List[Dict], labels: List[str], company_type: str
    ) -> ToolkitComposition:
        """Build asset composition (Chart 1) with Bank vs Non-Bank variants."""
        if company_type == "bank":
            # Bank variant mapping
            field_map = {
                "cash_short_invest": ["Tiền gửi tại NHNN (đồng)"],
                "receivable": ["Tiền gửi và cho vay tại các TCTD khác (đồng)"],
                "inventory": ["Cho vay khách hàng (đồng)"],
                "long_term_invest": ["Chứng khoán đầu tư (đồng)"],
                "total_asset": ["TỔNG CỘNG TÀI SẢN (đồng)"],
            }
            name_map = {
                "cash_short_invest": "Tiền gửi tại NHNN",
                "receivable": "Tiền gửi tại TCTD khác",
                "inventory": "Cho vay khách hàng",
                "long_term_invest": "Chứng khoán đầu tư",
                "other_asset": "Tài sản khác",
            }
        else:
            # Non-bank variant
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
            }

        reversed_data = list(reversed(balance_data))
        series_data: Dict[str, List[Optional[float]]] = {key: [] for key in field_map}
        series_data["other_asset"] = []

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

        series_keys = ["cash_short_invest", "receivable", "inventory", "long_term_invest", "other_asset"]
        series = [
            ToolkitSeriesItem(key=key, name=name_map[key], values=series_data[key])
            for key in series_keys
        ]

        percent_series = self._calc_percent_series(series_data, series_keys, "total_asset")

        return ToolkitComposition(labels=labels, series=series, percent_series=percent_series)

    def _build_liability_equity(
        self, balance_data: List[Dict], labels: List[str]
    ) -> ToolkitComposition:
        """Build liability & equity composition (Chart 2)."""
        field_map = {
            "equity": ["VỐN CHỦ SỞ HỮU (đồng)", "Vốn chủ sở hữu (đồng)", "Vốn chủ sở hữu"],
            "short_debt": ["Vay và nợ thuê tài chính ngắn hạn (đồng)", "Vay ngắn hạn (đồng)"],
            "long_debt": ["Vay và nợ thuê tài chính dài hạn (đồng)", "Vay dài hạn (đồng)"],
            "total_liabilities": ["NỢ PHẢI TRẢ (đồng)"],
            "total_sources": ["TỔNG CỘNG NGUỒN VỐN (đồng)"],
        }
        name_map = {
            "equity": "Vốn chủ sở hữu",
            "debt": "Nợ vay",
            "other_liabilities": "Nợ phải trả khác",
        }

        reversed_data = list(reversed(balance_data))
        series_data: Dict[str, List[Optional[float]]] = {
            "equity": [],
            "debt": [],
            "other_liabilities": [],
            "total_sources": [],
        }

        for item in reversed_data:
            # Equity
            equity = self._get_sum(item, field_map["equity"])
            series_data["equity"].append(equity)

            # Debt = short_debt + long_debt
            short_debt = self._get_sum(item, field_map["short_debt"])
            long_debt = self._get_sum(item, field_map["long_debt"])
            debt = None
            if short_debt is not None or long_debt is not None:
                debt = (short_debt or 0) + (long_debt or 0)
            series_data["debt"].append(debt)

            # Total sources
            total_sources = self._get_sum(item, field_map["total_sources"])
            series_data["total_sources"].append(total_sources)

            # Total liabilities
            total_liabilities = self._get_sum(item, field_map["total_liabilities"])

            # Fallback: liabilities = total_sources - equity
            if total_liabilities is None and total_sources is not None and equity is not None:
                total_liabilities = total_sources - equity

            # other_liabilities = total_liabilities - debt (or total_liabilities if debt missing)
            if total_liabilities is not None:
                other = total_liabilities - (debt or 0)
                series_data["other_liabilities"].append(other if other >= 0 else None)
            else:
                series_data["other_liabilities"].append(None)

        series_keys = ["equity", "debt", "other_liabilities"]
        series = [
            ToolkitSeriesItem(key=key, name=name_map[key], values=series_data[key])
            for key in series_keys
        ]

        percent_series = self._calc_percent_series(series_data, series_keys, "total_sources")

        return ToolkitComposition(labels=labels, series=series, percent_series=percent_series)

    def _build_revenue_composition_v2(
        self, income_data: List[Dict], labels: List[str]
    ) -> ToolkitComposition:
        """Build revenue composition (Chart 3) per toolkit.pdf spec."""
        # Per spec: gross_profit, financial_income, other_income
        field_map = {
            "gross_profit": ["Lãi gộp", "Lợi nhuận gộp (đồng)", "Lợi nhuận gộp"],
            "financial_income": ["Thu nhập tài chính", "Doanh thu hoạt động tài chính (đồng)", "Doanh thu tài chính"],
            "other_income": ["Thu nhập/Chi phí khác", "Thu nhập khác", "Thu nhập khác, ròng (đồng)", "Thu nhập khác (đồng)"],
        }
        name_map = {
            "gross_profit": "Lợi nhuận gộp",
            "financial_income": "Doanh thu tài chính",
            "other_income": "Thu nhập khác, ròng",
        }

        reversed_data = list(reversed(income_data))
        series_data: Dict[str, List[Optional[float]]] = {key: [] for key in field_map}

        for item in reversed_data:
            for key, fields in field_map.items():
                series_data[key].append(self._get_sum(item, fields))

        # Calculate total for percent
        total_key = "_total"
        series_data[total_key] = []
        for i in range(len(labels)):
            t = sum(
                series_data[k][i] or 0
                for k in field_map.keys()
                if i < len(series_data[k]) and series_data[k][i] is not None
            )
            series_data[total_key].append(t if t > 0 else None)

        series_keys = list(field_map.keys())
        series = [
            ToolkitSeriesItem(key=key, name=name_map[key], values=series_data[key])
            for key in series_keys
        ]

        percent_series = self._calc_percent_series(series_data, series_keys, total_key)

        return ToolkitComposition(labels=labels, series=series, percent_series=percent_series)

    def _build_expense_composition(
        self, income_data: List[Dict], labels: List[str]
    ) -> ToolkitComposition:
        """Build expense composition (Chart 4) per toolkit.pdf spec."""
        field_map = {
            "cogs": ["Giá vốn hàng bán", "Giá vốn hàng bán (đồng)"],
            "selling": ["Chi phí bán hàng", "Chi phí bán hàng (đồng)"],
            "admin": ["Chi phí quản lý DN", "Chi phí quản lý doanh nghiệp (đồng)", "Chi phí quản lý doanh nghiệp"],
            "interest": ["Chi phí tiền lãi vay", "Chi phí lãi vay (đồng)", "Chi phí lãi vay"],
        }
        name_map = {
            "cogs": "Giá vốn hàng bán",
            "selling": "Chi phí bán hàng",
            "admin": "Chi phí QLDN",
            "interest": "Chi phí lãi vay",
        }

        reversed_data = list(reversed(income_data))
        series_data: Dict[str, List[Optional[float]]] = {key: [] for key in field_map}

        for item in reversed_data:
            for key, fields in field_map.items():
                val = self._get_sum(item, fields)
                # Expenses are typically negative; take absolute value for stacked chart
                if val is not None:
                    val = abs(val)
                series_data[key].append(val)

        # Calculate total
        total_key = "_total"
        series_data[total_key] = []
        for i in range(len(labels)):
            t = sum(
                series_data[k][i] or 0
                for k in field_map.keys()
                if i < len(series_data[k]) and series_data[k][i] is not None
            )
            series_data[total_key].append(t if t > 0 else None)

        series_keys = list(field_map.keys())
        series = [
            ToolkitSeriesItem(key=key, name=name_map[key], values=series_data[key])
            for key in series_keys
        ]

        percent_series = self._calc_percent_series(series_data, series_keys, total_key)

        return ToolkitComposition(labels=labels, series=series, percent_series=percent_series)

    def _build_cfo_bridge(
        self, cash_flow_data: List[Dict], labels: List[str]
    ) -> ToolkitBridgeChart:
        """Build CFO bridge (Chart 5) per toolkit.pdf spec."""
        # (1) pre_tax_profit = Lợi nhuận trước thuế
        # (2) non_cash_adj = Khấu hao + FX +/- + thanh lý TSCĐ + (Lãi)/lỗ đầu tư + Thu lãi & cổ tức
        # (4) other_cash = Tiền lãi vay đã trả + Thuế TNDN đã nộp + Tiền chi khác cho HĐKD
        # (5) cfo = LƯU CHUYỂN TIỀN TỪ HOẠT ĐỘNG KINH DOANH
        # (3) working_cap_change = cfo - (1 + 2 + 4)

        reversed_data = list(reversed(cash_flow_data))
        pre_tax_profit = []
        non_cash_adj = []
        other_cash = []
        cfo = []
        working_cap_change = []

        for item in reversed_data:
            ptp = self._get_sum(item, ["Lãi/Lỗ ròng trước thuế", "Lợi nhuận trước thuế (đồng)"])
            pre_tax_profit.append(ptp)

            # Non-cash adjustments
            dep = self._get_sum(item, ["Khấu hao TSCĐ", "Khấu hao TSCĐ và BĐSĐT (đồng)"]) or 0
            fx = self._get_sum(item, ["Lãi/Lỗ chênh lệch tỷ giá chưa thực hiện", "(Lãi)/lỗ chênh lệch tỷ giá hối đoái chưa thực hiện (đồng)"]) or 0
            disposal = self._get_sum(item, ["Lãi/Lỗ từ thanh lý tài sản cố định", "(Lãi)/lỗ từ thanh lý TSCĐ (đồng)"]) or 0
            invest_income = self._get_sum(item, ["Lãi/Lỗ từ hoạt động đầu tư", "(Lãi)/lỗ từ hoạt động đầu tư (đồng)"]) or 0
            interest_div = self._get_sum(item, ["Thu lãi và cổ tức", "Chi phí lãi vay (đồng)"]) or 0
            nca = dep + fx + disposal + invest_income + interest_div
            non_cash_adj.append(nca if any([dep, fx, disposal, invest_income, interest_div]) else None)

            # Other cash items
            interest_paid = self._get_sum(item, ["Chi phí lãi vay đã trả", "Tiền lãi vay đã trả (đồng)"]) or 0
            tax_paid = self._get_sum(item, ["Tiền thu nhập doanh nghiệp đã trả", "Thuế TNDN đã nộp (đồng)"]) or 0
            other_op = self._get_sum(item, ["Tiền chi khác từ các hoạt động kinh doanh", "Tiền chi khác cho hoạt động kinh doanh (đồng)"]) or 0
            oc = interest_paid + tax_paid + other_op
            other_cash.append(oc if any([interest_paid, tax_paid, other_op]) else None)

            # CFO
            cfo_val = self._get_sum(item, ["Lưu chuyển tiền tệ ròng từ các hoạt động SXKD", "Lưu chuyển tiền thuần từ hoạt động kinh doanh (đồng)"])
            cfo.append(cfo_val)

            # Working capital change = CFO - (pre_tax + non_cash + other)
            if cfo_val is not None:
                wcc = cfo_val - ((ptp or 0) + (nca or 0) + (oc or 0))
                working_cap_change.append(wcc)
            else:
                working_cap_change.append(None)

        items = [
            ToolkitBridgeItem(key="pre_tax_profit", name="LN trước thuế", values=pre_tax_profit, bridge_type="start"),
            ToolkitBridgeItem(key="non_cash_adj", name="Điều chỉnh phi tiền mặt", values=non_cash_adj, bridge_type="flow"),
            ToolkitBridgeItem(key="working_cap_change", name="Thay đổi VLĐ", values=working_cap_change, bridge_type="flow"),
            ToolkitBridgeItem(key="other_cash", name="Tiền chi khác", values=other_cash, bridge_type="flow"),
            ToolkitBridgeItem(key="cfo", name="CFO", values=cfo, bridge_type="end"),
        ]

        return ToolkitBridgeChart(labels=labels, items=items)

    def _build_cfi_bridge(
        self, cash_flow_data: List[Dict], labels: List[str]
    ) -> ToolkitBridgeChart:
        """Build CFI bridge (Chart 6) per toolkit.pdf spec."""
        # (1) capex = Tiền chi mua sắm tài sản cố định
        # (2) asset_disposal = Tiền thu thanh lý, nhượng bán TSCĐ
        # (4) cfi = LƯU CHUYỂN TIỀN TỪ HOẠT ĐỘNG ĐẦU TƯ
        # (3) financial_invest = cfi - (1 + 2)

        reversed_data = list(reversed(cash_flow_data))
        capex = []
        asset_disposal = []
        cfi = []
        financial_invest = []

        for item in reversed_data:
            cap = self._get_sum(item, ["Mua sắm TSCĐ", "Tiền chi mua sắm, xây dựng TSCĐ và các TS dài hạn khác (đồng)"])
            capex.append(cap)

            disp = self._get_sum(item, ["Tiền thu được từ thanh lý tài sản cố định", "Tiền thu thanh lý, nhượng bán TSCĐ và các TS dài hạn khác (đồng)"])
            asset_disposal.append(disp)

            cfi_val = self._get_sum(item, ["Lưu chuyển từ hoạt động đầu tư", "Lưu chuyển tiền thuần từ hoạt động đầu tư (đồng)"])
            cfi.append(cfi_val)

            # financial_invest = CFI - (capex + disposal)
            if cfi_val is not None:
                fi = cfi_val - ((cap or 0) + (disp or 0))
                financial_invest.append(fi)
            else:
                financial_invest.append(None)

        items = [
            ToolkitBridgeItem(key="capex", name="Chi mua sắm TSCĐ", values=capex, bridge_type="start"),
            ToolkitBridgeItem(key="asset_disposal", name="Thu thanh lý TSCĐ", values=asset_disposal, bridge_type="flow"),
            ToolkitBridgeItem(key="financial_invest", name="ĐT tài chính", values=financial_invest, bridge_type="flow"),
            ToolkitBridgeItem(key="cfi", name="CFI", values=cfi, bridge_type="end"),
        ]

        return ToolkitBridgeChart(labels=labels, items=items)

    def _build_cff_bridge(
        self, cash_flow_data: List[Dict], labels: List[str]
    ) -> ToolkitBridgeChart:
        """Build CFF bridge (Chart 7) per toolkit.pdf spec."""
        # (2) equity_flow = Tiền thu phát hành CP + Tiền chi trả vốn góp, mua lại CP
        # (3) dividends = Cổ tức đã trả cho CSH
        # (4) cff = LƯU CHUYỂN TIỀN TỪ HOẠT ĐỘNG TÀI CHÍNH
        # (1) net_debt = cff - (2 + 3)

        reversed_data = list(reversed(cash_flow_data))
        net_debt = []
        equity_flow = []
        dividends = []
        cff = []

        for item in reversed_data:
            # Equity flow
            issue = self._get_sum(item, ["Tăng vốn cổ phần từ góp vốn và/hoặc phát hành cổ phiếu", "Tiền thu từ phát hành cổ phiếu, nhận vốn góp (đồng)"]) or 0
            buyback = self._get_sum(item, ["Chi trả cho việc mua lại, trả cổ phiếu", "Tiền chi trả vốn góp cho CSH, mua lại CP (đồng)"]) or 0
            ef = issue + buyback
            equity_flow.append(ef if any([issue, buyback]) else None)

            # Dividends
            div = self._get_sum(item, ["Cổ tức đã trả", "Cổ tức, lợi nhuận đã trả cho CSH (đồng)"])
            dividends.append(div)

            # CFF
            cff_val = self._get_sum(item, ["Lưu chuyển tiền từ hoạt động tài chính", "Lưu chuyển tiền thuần từ hoạt động tài chính (đồng)"])
            cff.append(cff_val)

            # net_debt = CFF - (equity_flow + dividends)
            if cff_val is not None:
                nd = cff_val - ((ef or 0) + (div or 0))
                net_debt.append(nd)
            else:
                net_debt.append(None)

        items = [
            ToolkitBridgeItem(key="net_debt", name="Vay ròng", values=net_debt, bridge_type="start"),
            ToolkitBridgeItem(key="equity_flow", name="Thu/Chi vốn góp", values=equity_flow, bridge_type="flow"),
            ToolkitBridgeItem(key="dividends", name="Cổ tức đã trả", values=dividends, bridge_type="flow"),
            ToolkitBridgeItem(key="cff", name="CFF", values=cff, bridge_type="end"),
        ]

        return ToolkitBridgeChart(labels=labels, items=items)

    def _build_net_cash_flow(
        self, cash_flow_data: List[Dict], labels: List[str]
    ) -> ToolkitNetCashFlow:
        """Build net cash flow (Chart 8) - delta_cash = cfo + cfi + cff."""
        reversed_data = list(reversed(cash_flow_data))
        cfo = []
        cfi = []
        cff = []
        delta_cash = []

        for item in reversed_data:
            cfo_val = self._get_sum(item, ["Lưu chuyển tiền tệ ròng từ các hoạt động SXKD", "Lưu chuyển tiền thuần từ hoạt động kinh doanh (đồng)"])
            cfi_val = self._get_sum(item, ["Lưu chuyển từ hoạt động đầu tư", "Lưu chuyển tiền thuần từ hoạt động đầu tư (đồng)"])
            cff_val = self._get_sum(item, ["Lưu chuyển tiền từ hoạt động tài chính", "Lưu chuyển tiền thuần từ hoạt động tài chính (đồng)"])

            cfo.append(cfo_val)
            cfi.append(cfi_val)
            cff.append(cff_val)

            # delta_cash = cfo + cfi + cff
            if any([cfo_val, cfi_val, cff_val]):
                dc = (cfo_val or 0) + (cfi_val or 0) + (cff_val or 0)
                delta_cash.append(dc)
            else:
                delta_cash.append(None)

        return ToolkitNetCashFlow(
            labels=labels,
            cfo=cfo,
            cfi=cfi,
            cff=cff,
            delta_cash=delta_cash,
        )

    def _get_sum(self, item: Dict, fields: List[str]) -> Optional[float]:
        """Get sum of numeric values from item for a list of candidate fields.

        vnstock/vci sometimes varies field names (e.g. with/without "(đồng)").
        This helper tries a couple of common variants per field.
        """
        total = 0.0
        has_value = False
        for field in fields:
            # try exact field and a normalized variant without (đồng)
            candidates = [field]
            if "(đồng)" in field:
                candidates.append(field.replace("(đồng)", "").strip())
            for k in candidates:
                val = item.get(k)
                if val is None or val == "":
                    continue
                try:
                    total += float(val)
                    has_value = True
                    break
                except (ValueError, TypeError):
                    continue
        return total if has_value else None

    def _calc_percent_series(
        self,
        series_data: Dict[str, List[Optional[float]]],
        keys: List[str],
        total_key: str,
    ) -> List[ToolkitPercentSeriesItem]:
        """Calculate percent series from series data."""
        percent_series = []
        for key in keys:
            pct_values = []
            for i, val in enumerate(series_data[key]):
                total = series_data[total_key][i] if i < len(series_data[total_key]) else None
                if val is not None and total and total != 0:
                    pct_values.append(val / total)
                else:
                    pct_values.append(None)
            percent_series.append(ToolkitPercentSeriesItem(key=key, values=pct_values))
        return percent_series


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

"""Vnstock financial and company data provider using vnstock."""
from typing import List, Optional, Dict, Any
from threading import Lock
import pandas as pd
import httpx

from app.core.logging import get_logger
from app.infrastructure.vnstock.instance_cache import get_company

logger = get_logger(__name__)

# Cache for vnstock Finance instances
_vnstock_finance_cache: Dict[str, Any] = {}
_vnstock_finance_lock = Lock()


def _get_vnstock_finance(symbol: str, period: str):
    """Get cached vnstock Finance instance."""
    key = f"{symbol.upper()}:{period}"
    if key not in _vnstock_finance_cache:
        with _vnstock_finance_lock:
            if key not in _vnstock_finance_cache:
                from vnstock import Finance
                _vnstock_finance_cache[key] = Finance(
                    symbol=symbol.upper(),
                    period=period,
                    source="vci"
                )
    return _vnstock_finance_cache[key]


class VnstockFinancialProvider:
    """Provider for vnstock financial data with year/quarter info."""

    def __init__(self, source: str = "vci"):
        self.source = source.lower()

    def get_balance_sheet(
        self, symbol: str, period: str, lang: str, limit: int
    ) -> List[Dict[str, Any]]:
        """Get balance sheet data."""
        try:
            finance = _get_vnstock_finance(symbol, period)
            df = finance.balance_sheet(lang=lang, dropna=True, to_df=True)

            if df is None or df.empty:
                return []

            if len(df) > limit:
                df = df.head(limit)

            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching balance sheet for {symbol}: {e}")
            return []

    def get_income_statement(
        self, symbol: str, period: str, lang: str, limit: int
    ) -> List[Dict[str, Any]]:
        """Get income statement data."""
        try:
            finance = _get_vnstock_finance(symbol, period)
            df = finance.income_statement(lang=lang, dropna=True, to_df=True)

            if df is None or df.empty:
                return []

            if len(df) > limit:
                df = df.head(limit)

            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching income statement for {symbol}: {e}")
            return []

    def get_cash_flow(
        self, symbol: str, period: str, lang: str, limit: int
    ) -> List[Dict[str, Any]]:
        """Get cash flow statement data."""
        try:
            finance = _get_vnstock_finance(symbol, period)
            df = finance.cash_flow(lang=lang, dropna=True, to_df=True)

            if df is None or df.empty:
                return []

            if len(df) > limit:
                df = df.head(limit)

            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching cash flow for {symbol}: {e}")
            return []

    def get_ratio(
        self, symbol: str, period: str, limit: int
    ) -> List[Dict[str, Any]]:
        """Get financial ratios."""
        try:
            finance = _get_vnstock_finance(symbol, period)
            df = finance.ratio(flatten_columns=True, separator="_", to_df=True)

            if df is None or df.empty:
                return []

            if len(df) > limit:
                df = df.head(limit)

            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching ratio for {symbol}: {e}")
            return []


class VnstockCompanyProvider:
    """Provider for vnstock_data company data."""
    
    def __init__(self, source: str = "vci"):
        self.source = source.lower()
    
    def get_overview(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company overview."""
        try:
            company = get_company(symbol, self.source)
            df = company.overview(to_df=True)
            
            if df is None or df.empty:
                return None
            
            return df.iloc[0].to_dict()
        except Exception as e:
            logger.error(f"Error fetching overview for {symbol}: {e}")
            return None
    
    def get_shareholders(self, symbol: str) -> List[Dict[str, Any]]:
        """Get shareholders data."""
        try:
            company = get_company(symbol, self.source)
            df = company.shareholders(to_df=True)
            
            if df is None or df.empty:
                return []
            
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching shareholders for {symbol}: {e}")
            return []
    
    def get_officers(self, symbol: str, filter_by: str = "working") -> List[Dict[str, Any]]:
        """Get officers data."""
        try:
            company = get_company(symbol, self.source)
            df = company.officers(filter_by=filter_by, to_df=True)
            
            if df is None or df.empty:
                return []
            
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching officers for {symbol}: {e}")
            return []
    
    def get_events(self, symbol: str) -> List[Dict[str, Any]]:
        """Get company events."""
        try:
            company = get_company(symbol, self.source)
            df = company.events(to_df=True)
            
            if df is None or df.empty:
                return []
            
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching events for {symbol}: {e}")
            return []
    
    def get_news(self, symbol: str) -> List[Dict[str, Any]]:
        """Get company news."""
        try:
            company = get_company(symbol, self.source)
            df = company.news(to_df=True)
            
            if df is None or df.empty:
                return []
            
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []
    
    def get_subsidiaries(self, symbol: str, filter_by: str = "all") -> List[Dict[str, Any]]:
        """Get subsidiaries data."""
        try:
            company = get_company(symbol, self.source)
            df = company.subsidiaries(filter_by=filter_by, to_df=True)
            
            if df is None or df.empty:
                return []
            
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching subsidiaries for {symbol}: {e}")
            return []
    
    def get_trading_stats(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get trading statistics including foreign ownership."""
        try:
            company = get_company(symbol, self.source)
            df = company.trading_stats()
            
            if df is None or df.empty:
                return None
            
            return df.iloc[0].to_dict()
        except Exception as e:
            logger.error(f"Error fetching trading stats for {symbol}: {e}")
            return None
    
    def get_ratio_summary(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get ratio summary including market cap, PE, PB, EPS, etc."""
        try:
            company = get_company(symbol, self.source)
            df = company.ratio_summary()
            
            if df is None or df.empty:
                return None
            
            return df.iloc[0].to_dict()
        except Exception as e:
            logger.error(f"Error fetching ratio summary for {symbol}: {e}")
            return None
    
    def get_analysis_reports(
        self, symbol: str, page: int = 0, size: int = 20
    ) -> Dict[str, Any]:
        """Get analysis reports from Simplize API."""
        try:
            url = "https://api2.simplize.vn/api/company/analysis-report/list"
            params = {
                "ticker": symbol.upper(),
                "isWl": "false",
                "page": page,
                "size": size,
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                result = response.json()
                
                return {
                    "status": result.get("status"),
                    "message": result.get("message"),
                    "total": result.get("total", 0),
                    "data": result.get("data", []),
                }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching analysis reports for {symbol}: {e}")
            return {"status": e.response.status_code, "message": str(e), "total": 0, "data": []}
        except httpx.RequestError as e:
            logger.error(f"Request error fetching analysis reports for {symbol}: {e}")
            return {"status": 500, "message": str(e), "total": 0, "data": []}
        except Exception as e:
            logger.error(f"Error fetching analysis reports for {symbol}: {e}")
            return {"status": 500, "message": str(e), "total": 0, "data": []}

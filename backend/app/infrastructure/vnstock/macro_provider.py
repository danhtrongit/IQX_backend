"""Vnstock macro data provider using vnstock_data."""
from typing import List, Dict, Any
import numpy as np

from app.core.logging import get_logger
from app.infrastructure.vnstock.instance_cache import get_macro

logger = get_logger(__name__)


class VnstockMacroProvider:
    """Provider for Vietnamese macroeconomic data from vnstock_data."""

    def __init__(self, source: str = "mbk"):
        self.source = source.lower()

    def get_gdp(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get GDP (Gross Domestic Product) data."""
        try:
            macro = get_macro(self.source)
            df = macro.gdp(limit=limit, to_df=True)
            if df is None or df.empty:
                return []
            df = df.replace({np.nan: None})
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching GDP data: {e}")
            return []

    def get_cpi(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get CPI (Consumer Price Index) data."""
        try:
            macro = get_macro(self.source)
            df = macro.cpi(limit=limit, to_df=True)
            if df is None or df.empty:
                return []
            df = df.replace({np.nan: None})
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching CPI data: {e}")
            return []

    def get_exchange_rate(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get USD/VND exchange rate data."""
        try:
            macro = get_macro(self.source)
            df = macro.exchange_rate(limit=limit, to_df=True)
            if df is None or df.empty:
                return []
            df = df.replace({np.nan: None})
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching exchange rate data: {e}")
            return []

    def get_import_export(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get import/export trade data."""
        try:
            macro = get_macro(self.source)
            df = macro.import_export(limit=limit, to_df=True)
            if df is None or df.empty:
                return []
            df = df.replace({np.nan: None})
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching import/export data: {e}")
            return []

    def get_fdi(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get FDI (Foreign Direct Investment) data."""
        try:
            macro = get_macro(self.source)
            df = macro.fdi(limit=limit, to_df=True)
            if df is None or df.empty:
                return []
            df = df.replace({np.nan: None})
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching FDI data: {e}")
            return []

    def get_money_supply(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get money supply M2 data."""
        try:
            macro = get_macro(self.source)
            df = macro.money_supply(limit=limit, to_df=True)
            if df is None or df.empty:
                return []
            df = df.replace({np.nan: None})
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching money supply data: {e}")
            return []

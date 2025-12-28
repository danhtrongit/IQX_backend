"""Vnstock commodity data provider implementation using vnstock_data."""
from typing import List, Optional, Dict, Any
import pandas as pd

from app.core.logging import get_logger
from app.infrastructure.vnstock.instance_cache import get_commodity

logger = get_logger(__name__)


class VnstockCommodityProvider:
    """Provider for vnstock_data commodity price data."""

    def __init__(self, source: str = "spl"):
        self.source = source.lower()

    def get_gold_vn(self, limit: int = 100) -> List[dict]:
        """Get Vietnam gold prices (buy, sell)."""
        try:
            commodity = get_commodity(self.source)
            df = commodity.gold_vn(to_df=True)

            if df is None or df.empty:
                return []

            # Apply limit
            if limit and len(df) > limit:
                df = df.tail(limit)

            return self._process_dataframe(df)
        except Exception as e:
            logger.error(f"Error fetching Vietnam gold prices: {e}")
            return []

    def get_gold_global(self, limit: int = 100) -> List[dict]:
        """Get global gold prices."""
        try:
            commodity = get_commodity(self.source)
            df = commodity.gold_global(to_df=True)

            if df is None or df.empty:
                return []

            # Apply limit
            if limit and len(df) > limit:
                df = df.tail(limit)

            return self._process_dataframe(df)
        except Exception as e:
            logger.error(f"Error fetching global gold prices: {e}")
            return []

    def get_oil_crude(self, limit: int = 100) -> List[dict]:
        """Get crude oil prices."""
        try:
            commodity = get_commodity(self.source)
            df = commodity.oil_crude(to_df=True)

            if df is None or df.empty:
                return []

            # Apply limit
            if limit and len(df) > limit:
                df = df.tail(limit)

            return self._process_dataframe(df)
        except Exception as e:
            logger.error(f"Error fetching crude oil prices: {e}")
            return []

    def get_gas_natural(self, limit: int = 100) -> List[dict]:
        """Get natural gas prices."""
        try:
            commodity = get_commodity(self.source)
            df = commodity.gas_natural(to_df=True)

            if df is None or df.empty:
                return []

            # Apply limit
            if limit and len(df) > limit:
                df = df.tail(limit)

            return self._process_dataframe(df)
        except Exception as e:
            logger.error(f"Error fetching natural gas prices: {e}")
            return []

    def get_steel_hrc(self, limit: int = 100) -> List[dict]:
        """Get steel HRC prices."""
        try:
            commodity = get_commodity(self.source)
            df = commodity.steel_hrc(to_df=True)

            if df is None or df.empty:
                return []

            # Apply limit
            if limit and len(df) > limit:
                df = df.tail(limit)

            return self._process_dataframe(df)
        except Exception as e:
            logger.error(f"Error fetching steel HRC prices: {e}")
            return []

    def get_steel_d10(self, limit: int = 100) -> List[dict]:
        """Get steel D10 prices."""
        try:
            commodity = get_commodity(self.source)
            df = commodity.steel_d10(to_df=True)

            if df is None or df.empty:
                return []

            # Apply limit
            if limit and len(df) > limit:
                df = df.tail(limit)

            return self._process_dataframe(df)
        except Exception as e:
            logger.error(f"Error fetching steel D10 prices: {e}")
            return []

    @staticmethod
    def _process_dataframe(df: pd.DataFrame) -> List[dict]:
        """Process DataFrame and convert to list of dicts."""
        import numpy as np

        # Replace NaN with None for JSON serialization
        df = df.replace({np.nan: None})

        return df.to_dict(orient="records")

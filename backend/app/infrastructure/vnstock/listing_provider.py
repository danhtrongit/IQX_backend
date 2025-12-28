"""Vnstock listing data provider using vnstock_data with instance caching."""
from typing import List, Dict, Any
import pandas as pd
import numpy as np

from app.core.logging import get_logger
from app.infrastructure.vnstock.instance_cache import get_listing

logger = get_logger(__name__)


class VnstockListingProvider:
    """Provider for vnstock_data listing data."""
    
    def __init__(self, source: str = "vci"):
        self.source = source.lower()
    
    def get_stocks(self) -> List[Dict[str, Any]]:
        """Get all stock symbols."""
        try:
            listing = get_listing(self.source)
            df = listing.symbols_by_exchange(lang="vi", to_df=True)
            if df is None or df.empty:
                return []
            df = df.astype(object)
            df = df.where(pd.notnull(df), None)
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching stocks: {e}")
            return []
            
    def get_etfs(self) -> List[Dict[str, Any]]:
        """Get all ETFs."""
        try:
            listing = get_listing(self.source)
            # ETFs are typically in symbols_by_group with group="ETF"
            df = listing.symbols_by_group(group="ETF", to_df=True)
            if df is None or df.empty:
                return []
            df = df.astype(object)
            df = df.where(pd.notnull(df), None)
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching ETFs: {e}")
            return []

    def get_industries(self) -> List[Dict[str, Any]]:
        """Get symbols by industries."""
        try:
            listing = get_listing(self.source)
            df = listing.symbols_by_industries(lang="vi", to_df=True)
            if df is None or df.empty:
                return []
            df = df.astype(object)
            df = df.where(pd.notnull(df), None)
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching industries: {e}")
            return []

    def get_industries_icb(self) -> List[Dict[str, Any]]:
        """Get ICB classification."""
        try:
            listing = get_listing(self.source)
            df = listing.industries_icb(to_df=True)
            if df is None or df.empty:
                return []
            df = df.astype(object)
            df = df.where(pd.notnull(df), None)
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching ICB: {e}")
            return []

    def get_symbols_by_group(self, group: str = "VN30") -> List[Dict[str, Any]]:
        """Get symbols by group (VN30, HNX30, VNMID, VN100, etc.)."""
        try:
            listing = get_listing(self.source)
            df = listing.symbols_by_group(group=group, to_df=True)
            if df is None or df.empty:
                return []
            df = df.astype(object)
            df = df.where(pd.notnull(df), None)
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching symbols by group {group}: {e}")
            return []

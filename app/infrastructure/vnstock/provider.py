"""Vnstock data provider implementation."""
from typing import List, Optional
import pandas as pd

from app.core.logging import get_logger

logger = get_logger(__name__)


class VnstockProvider:
    """Provider for vnstock data."""
    
    def __init__(self, source: str = "vci"):
        self.source = source.lower()
        self._listing = None
        self._company_class = None
    
    def _get_listing(self):
        """Lazy load listing module."""
        if self._listing is None:
            from vnstock_data.api.listing import Listing
            self._listing = Listing(source=self.source, show_log=False)
        return self._listing
    
    def _get_company_class(self):
        """Lazy load company class."""
        if self._company_class is None:
            from vnstock_data.api.company import Company
            self._company_class = Company
        return self._company_class
    
    def get_all_symbols(self) -> List[dict]:
        """Get all symbols with exchange info."""
        try:
            listing = self._get_listing()
            df = listing.symbols_by_exchange(lang="vi", to_df=True)
            
            if df is None or df.empty:
                return []
            
            # Rename columns to match our schema
            df = df.rename(columns={
                "organ_short_name": "organ_short_name",
            })
            
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching symbols: {e}")
            return []
    
    def get_symbols_by_industries(self) -> List[dict]:
        """Get symbols with industry classification."""
        try:
            listing = self._get_listing()
            df = listing.symbols_by_industries(lang="vi", to_df=True)
            
            if df is None or df.empty:
                return []
            
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching industries: {e}")
            return []
    
    def get_industries_icb(self) -> List[dict]:
        """Get ICB industry hierarchy."""
        try:
            listing = self._get_listing()
            df = listing.industries_icb(to_df=True)
            
            if df is None or df.empty:
                return []
            
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching ICB: {e}")
            return []
    
    def get_company_overview(self, symbol: str) -> Optional[dict]:
        """Get company overview details."""
        try:
            Company = self._get_company_class()
            company = Company(source=self.source, symbol=symbol, show_log=False)
            df = company.overview()
            
            if df is None or df.empty:
                return None
            
            return df.iloc[0].to_dict()
        except Exception as e:
            logger.debug(f"Error fetching company {symbol}: {e}")
            return None

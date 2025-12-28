"""Vnstock market data provider using vnstock_data."""
from typing import List, Dict, Any
import numpy as np

from app.core.logging import get_logger
from app.infrastructure.vnstock.instance_cache import get_market

logger = get_logger(__name__)


class VnstockMarketProvider:
    """Provider for vnstock_data market data."""
    
    def __init__(self, source: str = "vnd"):
        self.source = source.lower()
        
    def get_evaluation(self, period: str = 'day', time_window: str = '1D') -> List[Dict[str, Any]]:
        """Get market evaluation (PE, PB, etc.)."""
        try:
            market = get_market(self.source)
            df = market.evaluation(period=period, time_window=time_window, to_df=True)
            if df is None or df.empty:
                return []
            df = df.replace({np.nan: None})
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching market evaluation: {e}")
            return []
    
    def get_pe(self, duration: str = '5Y') -> List[Dict[str, Any]]:
        """Get P/E ratio data."""
        try:
            market = get_market(self.source)
            df = market.pe(duration=duration, to_df=True)
            if df is None or df.empty:
                return []
            df = df.replace({np.nan: None})
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching PE data: {e}")
            return []
    
    def get_pb(self, duration: str = '5Y') -> List[Dict[str, Any]]:
        """Get P/B ratio data."""
        try:
            market = get_market(self.source)
            df = market.pb(duration=duration, to_df=True)
            if df is None or df.empty:
                return []
            df = df.replace({np.nan: None})
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching PB data: {e}")
            return []

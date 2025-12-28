"""Market application services."""
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from app.core.logging import get_logger
from app.core.async_utils import run_sync, run_parallel
from app.application.market.dtos import (
    IndexResponse,
    MarketOverviewResponse,
    IndexHistoryRequest,
    IndexHistoryItem,
    IndexHistoryResponse,
    MarketEvaluationResponse,
    MarketEvaluationItem
)
from app.infrastructure.vnstock.instance_cache import get_quote, get_market

logger = get_logger(__name__)

# Index codes
INDEX_CODES = ["VNINDEX", "HNXINDEX", "UPCOMINDEX", "VN30"]


def _fetch_index_sync(index_code: str) -> Optional[Dict]:
    """Sync function to fetch single index data."""
    try:
        quote = get_quote(index_code)
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        df = quote.history(
            start=start_date,
            end=end_date,
            interval="1D",
            count_back=2,
        )
        
        if df is None or df.empty:
            return None
        
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        close_val = float(latest.get("close", 0))
        prev_close = float(prev.get("close", close_val))
        change = close_val - prev_close
        change_pct = (change / prev_close * 100) if prev_close else 0
        
        return {
            "index_code": index_code,
            "index_value": close_val,
            "change": round(change, 2),
            "change_percent": round(change_pct, 2),
            "ref_value": prev_close,
            "open_value": float(latest.get("open", 0)),
            "high_value": float(latest.get("high", 0)),
            "low_value": float(latest.get("low", 0)),
            "total_volume": int(latest.get("volume", 0)),
            "timestamp": datetime.utcnow(),
        }
    except Exception as e:
        logger.error(f"Error fetching index {index_code}: {e}")
        return None


class MarketService:
    """Market service for index and market overview data."""
    
    async def get_market_overview(self) -> MarketOverviewResponse:
        """
        Get market overview with all major indices.
        Fetches all indices in PARALLEL for better performance.
        """
        # Run all index fetches in parallel
        results = await run_parallel(*[
            lambda ic=ic: _fetch_index_sync(ic) for ic in INDEX_CODES
        ])
        
        indices = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error fetching {INDEX_CODES[i]}: {result}")
            elif result:
                indices.append(IndexResponse(**result))
        
        return MarketOverviewResponse(
            indices=indices,
            timestamp=datetime.utcnow(),
        )
    
    async def get_index(self, index_code: str) -> Optional[IndexResponse]:
        """Get single index data."""
        index_code = index_code.upper()
        
        # Try to get from WebSocket cache first
        try:
            from app.infrastructure.streaming.price_stream import price_stream_manager
            cached = price_stream_manager.get_cached_index(index_code)
            if cached:
                return IndexResponse(
                    index_code=index_code,
                    index_value=cached.current_index,
                    change=cached.change,
                    change_percent=cached.percent_change,
                    open_value=cached.open_index,
                    total_volume=cached.volume,
                    total_value=cached.value,
                    advances=cached.advances,
                    declines=cached.declines,
                    unchanged=cached.unchanged,
                    timestamp=datetime.fromtimestamp(cached.timestamp),
                )
        except Exception:
            pass
        
        # Fallback to REST API
        result = await run_sync(_fetch_index_sync, index_code)
        if result:
            return IndexResponse(**result)
        return None
    
    async def get_index_history(
        self, index_code: str, request: IndexHistoryRequest
    ) -> IndexHistoryResponse:
        """Get index historical data."""
        index_code = index_code.upper()
        
        def _fetch():
            try:
                quote = get_quote(index_code)
                df = quote.history(
                    start=request.start,
                    end=request.end,
                    interval=request.interval,
                )
                
                if df is None or df.empty:
                    return []
                
                items = []
                for _, row in df.iterrows():
                    items.append({
                        "time": row.get("time"),
                        "open": float(row.get("open", 0)),
                        "high": float(row.get("high", 0)),
                        "low": float(row.get("low", 0)),
                        "close": float(row.get("close", 0)),
                        "volume": int(row.get("volume", 0)),
                    })
                return items
            except Exception as e:
                logger.error(f"Error fetching index history {index_code}: {e}")
                return []
        
        items_data = await run_sync(_fetch)
        items = [IndexHistoryItem(**item) for item in items_data]
        
        return IndexHistoryResponse(
            index_code=index_code,
            data=items,
            count=len(items),
        )
            
    async def get_evaluation(self, period: str = 'day', time_window: str = '1D') -> MarketEvaluationResponse:
        """Get market evaluation."""
        def _fetch():
            try:
                import numpy as np
                market = get_market()
                df = market.evaluation(period=period, time_window=time_window, to_df=True)
                if df is None or df.empty:
                    return []
                df = df.replace({np.nan: None})
                return df.to_dict(orient="records")
            except Exception as e:
                logger.error(f"Error fetching market evaluation: {e}")
                return []
        
        data = await run_sync(_fetch)
        
        items = []
        for row in data:
            pe = row.get("pe") if "pe" in row else row.get("PE")
            pb = row.get("pb") if "pb" in row else row.get("PB")
            date_val = row.get("fromDate") if "fromDate" in row else row.get("date")
            
            items.append(MarketEvaluationItem(
                date=str(date_val) if date_val else None,
                pe=self._safe_float(pe),
                pb=self._safe_float(pb),
                vn_type=row.get("vn_type")
            ))
        return MarketEvaluationResponse(data=items, count=len(items))

    @staticmethod
    def _safe_float(val: Any) -> Optional[float]:
        if val is None:
            return None
        try:
            return float(val)
        except:
            return None

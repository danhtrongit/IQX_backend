"""Quote application services."""
from typing import Optional, List, Protocol
from datetime import datetime

from app.application.quote.dtos import (
    HistoryRequest,
    IntradayRequest,
    PriceBoardRequest,
    TradingStatsRequest,
    OHLCVItem,
    HistoryResponse,
    IntradayItem,
    IntradayResponse,
    PriceInfo,
    PriceBoardResponse,
    PriceDepthItem,
    PriceDepthResponse,
    TradingStatsItem,
    TradingStatsResponse,
)
from app.core.errors import AppError


class QuoteDataProvider(Protocol):
    """Quote data provider interface."""
    
    def get_history(
        self,
        symbol: str,
        start: str,
        end: Optional[str],
        interval: str,
        count_back: Optional[int],
    ) -> List[dict]:
        """Get historical OHLCV data."""
        ...
    
    def get_intraday(
        self,
        symbol: str,
        page_size: int,
        last_time: Optional[str],
    ) -> List[dict]:
        """Get intraday trades."""
        ...
    
    def get_price_board(self, symbols: List[str]) -> List[dict]:
        """Get price board for multiple symbols."""
        ...
    
    def get_price_depth(self, symbol: str) -> List[dict]:
        """Get price depth."""
        ...
    
    def get_trading_stats(
        self,
        symbol: str,
        resolution: str,
        start: Optional[str],
        end: Optional[str],
        limit: int,
    ) -> List[dict]:
        """Get trading statistics."""
        ...


class QuoteService:
    """Quote service."""
    
    def __init__(self, data_provider: QuoteDataProvider):
        self.data_provider = data_provider
    
    def get_history(self, symbol: str, request: HistoryRequest) -> HistoryResponse:
        """Get historical OHLCV data."""
        data = self.data_provider.get_history(
            symbol=symbol.upper(),
            start=request.start,
            end=request.end,
            interval=request.interval,
            count_back=request.count_back,
        )
        
        items = []
        for row in data:
            items.append(OHLCVItem(
                time=self._parse_datetime(row.get("time")),
                open=float(row.get("open", 0)),
                high=float(row.get("high", 0)),
                low=float(row.get("low", 0)),
                close=float(row.get("close", 0)),
                volume=int(row.get("volume", 0)),
            ))
        
        return HistoryResponse(
            symbol=symbol.upper(),
            interval=request.interval,
            data=items,
            count=len(items),
        )
    
    def get_intraday(self, symbol: str, request: IntradayRequest) -> IntradayResponse:
        """Get intraday trades."""
        data = self.data_provider.get_intraday(
            symbol=symbol.upper(),
            page_size=request.page_size,
            last_time=request.last_time,
        )
        
        items = []
        for row in data:
            items.append(IntradayItem(
                time=self._parse_datetime(row.get("time")),
                price=float(row.get("price", 0)),
                volume=int(row.get("volume", 0)),
                side=row.get("side"),
            ))
        
        return IntradayResponse(
            symbol=symbol.upper(),
            data=items,
            count=len(items),
        )
    
    def get_price_board(self, request: PriceBoardRequest) -> PriceBoardResponse:
        """Get price board for multiple symbols."""
        # Filter valid symbols: non-empty, alphanumeric, 1-10 chars
        symbols = [
            s.upper().strip()
            for s in request.symbols
            if s and s.strip() and s.strip().isalnum() and 1 <= len(s.strip()) <= 10
        ]
        
        if not symbols:
            return PriceBoardResponse(data=[], count=0)
        
        data = self.data_provider.get_price_board(symbols)
        
        items = []
        for row in data:
            # Skip rows without valid symbol
            symbol = row.get("symbol")
            if not symbol:
                continue
            
            items.append(PriceInfo(
                symbol=symbol,
                exchange=row.get("exchange"),
                organ_name=row.get("organ_name"),
                price=self._safe_float(row.get("price")),
                change=self._safe_float(row.get("change")),
                change_percent=self._safe_float(row.get("change_percent")),
                volume=self._safe_int(row.get("volume")),
                value=self._safe_float(row.get("value")),
                ref_price=self._safe_float(row.get("ref_price")),
                ceiling=self._safe_float(row.get("ceiling")),
                floor=self._safe_float(row.get("floor")),
                open=self._safe_float(row.get("open")),
                high=self._safe_float(row.get("high")),
                low=self._safe_float(row.get("low")),
                bid_1_price=self._safe_float(row.get("bid_1_price")),
                bid_1_volume=self._safe_int(row.get("bid_1_volume")),
                bid_2_price=self._safe_float(row.get("bid_2_price")),
                bid_2_volume=self._safe_int(row.get("bid_2_volume")),
                bid_3_price=self._safe_float(row.get("bid_3_price")),
                bid_3_volume=self._safe_int(row.get("bid_3_volume")),
                ask_1_price=self._safe_float(row.get("ask_1_price")),
                ask_1_volume=self._safe_int(row.get("ask_1_volume")),
                ask_2_price=self._safe_float(row.get("ask_2_price")),
                ask_2_volume=self._safe_int(row.get("ask_2_volume")),
                ask_3_price=self._safe_float(row.get("ask_3_price")),
                ask_3_volume=self._safe_int(row.get("ask_3_volume")),
                foreign_buy_volume=self._safe_int(row.get("foreign_buy_volume")),
                foreign_sell_volume=self._safe_int(row.get("foreign_sell_volume")),
            ))
        
        return PriceBoardResponse(data=items, count=len(items))
    
    def get_price_depth(self, symbol: str) -> PriceDepthResponse:
        """Get price depth."""
        data = self.data_provider.get_price_depth(symbol.upper())
        
        items = []
        for row in data:
            items.append(PriceDepthItem(
                price=float(row.get("price", 0)),
                volume=int(float(row.get("volume", 0))),
                buy_volume=self._safe_int(row.get("buy_volume")),
                sell_volume=self._safe_int(row.get("sell_volume")),
            ))
        
        return PriceDepthResponse(symbol=symbol.upper(), data=items)
    
    def get_trading_stats(
        self,
        symbol: str,
        request: TradingStatsRequest,
    ) -> TradingStatsResponse:
        """Get trading statistics."""
        data = self.data_provider.get_trading_stats(
            symbol=symbol.upper(),
            resolution=request.resolution,
            start=request.start,
            end=request.end,
            limit=request.limit,
        )
        
        items = []
        for row in data:
            items.append(TradingStatsItem(
                trading_date=self._parse_datetime(row.get("trading_date")),
                open=self._safe_float(row.get("open")),
                high=self._safe_float(row.get("high")),
                low=self._safe_float(row.get("low")),
                close=self._safe_float(row.get("close")),
                matched_volume=self._safe_int(row.get("matched_volume")),
                matched_value=self._safe_float(row.get("matched_value")),
                deal_volume=self._safe_int(row.get("deal_volume")),
                deal_value=self._safe_float(row.get("deal_value")),
            ))
        
        return TradingStatsResponse(
            symbol=symbol.upper(),
            data=items,
            count=len(items),
        )
    
    @staticmethod
    def _parse_datetime(value) -> datetime:
        if value is None:
            return datetime.utcnow()
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return datetime.strptime(value[:19], "%Y-%m-%d %H:%M:%S")
        return datetime.utcnow()
    
    @staticmethod
    def _safe_float(value) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _safe_int(value) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None

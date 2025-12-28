
"""Insight/Analysis application services."""

from typing import Optional, List, Protocol, Dict, Any
from datetime import datetime

from app.application.insight.dtos import (
    TopForeignItem,
    TopForeignResponse,
    TopStockResponse,
    ProprietaryTradingItem,
    ProprietaryTradingResponse,
    ForeignTradingItem,
    ForeignTradingResponse,
    OrderStatsResponse,
    SideStatsResponse,
    InsiderTradingItem,
    InsiderTradingResponse,
)


class InsightDataProvider(Protocol):
    """Insight data provider interface."""

    def get_top_foreign_buy(
        self, date: Optional[str], limit: int
    ) -> List[Dict[str, Any]]:
        ...

    def get_top_foreign_sell(
        self, date: Optional[str], limit: int
    ) -> List[Dict[str, Any]]:
        ...

    def get_top_gainer(self, index: str, limit: int) -> List[Dict[str, Any]]:
        ...

    def get_top_loser(self, index: str, limit: int) -> List[Dict[str, Any]]:
        ...

    def get_top_value(self, index: str, limit: int) -> List[Dict[str, Any]]:
        ...

    def get_top_volume(self, index: str, limit: int) -> List[Dict[str, Any]]:
        ...

    def get_top_deal(self, index: str, limit: int) -> List[Dict[str, Any]]:
        ...


class TradingInsightProvider(Protocol):
    """Trading insight provider interface."""

    def get_proprietary_trading(
        self,
        symbol: str,
        start: Optional[str],
        end: Optional[str],
        limit: int,
    ) -> List[Dict[str, Any]]:
        ...

    def get_foreign_trading(
        self,
        symbol: str,
        start: Optional[str],
        end: Optional[str],
        limit: int,
    ) -> List[Dict[str, Any]]:
        ...
        
    def get_order_stats(self, symbol: str) -> List[Dict[str, Any]]: ...
    def get_side_stats(self, symbol: str) -> List[Dict[str, Any]]: ...

    def get_insider_trading(
        self,
        symbol: str,
        start: Optional[str],
        end: Optional[str],
        limit: int,
    ) -> List[Dict[str, Any]]:
        ...


class InsightService:
    """Market insight service."""

    def __init__(self, data_provider: InsightDataProvider):
        self.data_provider = data_provider

    def get_top_foreign_buy(
        self, date: Optional[str] = None, limit: int = 10
    ) -> TopForeignResponse:
        """Get top foreign net buy stocks."""
        data = self.data_provider.get_top_foreign_buy(date=date, limit=limit)
        items = [
            TopForeignItem(
                symbol=row.get("symbol", ""),
                date=row.get("date"),
                net_value=self._safe_float(row.get("net_value")),
            )
            for row in data
        ]
        return TopForeignResponse(
            type="buy",
            date=date or datetime.now().strftime("%Y-%m-%d"),
            data=items,
            count=len(items),
        )

    def get_top_foreign_sell(
        self, date: Optional[str] = None, limit: int = 10
    ) -> TopForeignResponse:
        """Get top foreign net sell stocks."""
        data = self.data_provider.get_top_foreign_sell(date=date, limit=limit)
        items = [
            TopForeignItem(
                symbol=row.get("symbol", ""),
                date=row.get("date"),
                net_value=self._safe_float(row.get("net_value")),
            )
            for row in data
        ]
        return TopForeignResponse(
            type="sell",
            date=date or datetime.now().strftime("%Y-%m-%d"),
            data=items,
            count=len(items),
        )

    def get_top_gainer(
        self, index: str = "VNINDEX", limit: int = 10
    ) -> TopStockResponse:
        """Get top gaining stocks."""
        data = self.data_provider.get_top_gainer(index=index, limit=limit)
        return TopStockResponse(
            type="gainer",
            index=index,
            data=data,
            count=len(data),
        )

    def get_top_loser(
        self, index: str = "VNINDEX", limit: int = 10
    ) -> TopStockResponse:
        """Get top losing stocks."""
        data = self.data_provider.get_top_loser(index=index, limit=limit)
        return TopStockResponse(
            type="loser",
            index=index,
            data=data,
            count=len(data),
        )

    def get_top_value(
        self, index: str = "VNINDEX", limit: int = 10
    ) -> TopStockResponse:
        """Get top stocks by trading value."""
        data = self.data_provider.get_top_value(index=index, limit=limit)
        return TopStockResponse(
            type="value",
            index=index,
            data=data,
            count=len(data),
        )

    def get_top_volume(
        self, index: str = "VNINDEX", limit: int = 10
    ) -> TopStockResponse:
        """Get top stocks by abnormal volume."""
        data = self.data_provider.get_top_volume(index=index, limit=limit)
        return TopStockResponse(
            type="volume",
            index=index,
            data=data,
            count=len(data),
        )

    def get_top_deal(
        self, index: str = "VNINDEX", limit: int = 10
    ) -> TopStockResponse:
        """Get top stocks by block deal."""
        data = self.data_provider.get_top_deal(index=index, limit=limit)
        return TopStockResponse(
            type="deal",
            index=index,
            data=data,
            count=len(data),
        )

    @staticmethod
    def _safe_float(value) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None


class TradingInsightService:
    """Trading insight service (per symbol)."""

    def __init__(self, data_provider: TradingInsightProvider):
        self.data_provider = data_provider

    def get_proprietary_trading(
        self,
        symbol: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 30,
    ) -> ProprietaryTradingResponse:
        """Get proprietary trading history for a symbol."""
        data = self.data_provider.get_proprietary_trading(
            symbol=symbol.upper(),
            start=start,
            end=end,
            limit=limit,
        )
        items = [ProprietaryTradingItem(**row) for row in data]
        return ProprietaryTradingResponse(
            symbol=symbol.upper(),
            data=items,
            count=len(items),
        )

    def get_foreign_trading(
        self,
        symbol: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 30,
    ) -> ForeignTradingResponse:
        """Get foreign trading history for a symbol."""
        data = self.data_provider.get_foreign_trading(
            symbol=symbol.upper(),
            start=start,
            end=end,
            limit=limit,
        )
        items = [ForeignTradingItem(**row) for row in data]
        return ForeignTradingResponse(
            symbol=symbol.upper(),
            data=items,
            count=len(items),
        )

    def get_order_stats(self, symbol: str) -> OrderStatsResponse:
        data = self.data_provider.get_order_stats(symbol.upper())
        return OrderStatsResponse(symbol=symbol.upper(), data=data, count=len(data))

    def get_side_stats(self, symbol: str) -> SideStatsResponse:
        data = self.data_provider.get_side_stats(symbol.upper())
        return SideStatsResponse(symbol=symbol.upper(), data=data, count=len(data))

    def get_insider_trading(
        self,
        symbol: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 30,
    ) -> InsiderTradingResponse:
        """Get insider trading history for a symbol."""
        data = self.data_provider.get_insider_trading(
            symbol=symbol.upper(),
            start=start,
            end=end,
            limit=limit,
        )
        items = [InsiderTradingItem(**row) for row in data]
        return InsiderTradingResponse(
            symbol=symbol.upper(),
            data=items,
            count=len(items),
        )

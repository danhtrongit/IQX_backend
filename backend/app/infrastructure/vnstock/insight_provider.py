"""Vnstock insight/analysis data provider using vnstock_data."""
from typing import List, Dict, Any, Optional
import pandas as pd

from app.core.logging import get_logger
from app.infrastructure.vnstock.instance_cache import get_top_stock, get_trading_explorer, get_trading

logger = get_logger(__name__)


class VnstockInsightProvider:
    """Provider for market insight/analysis data from vnstock_data."""

    def get_top_foreign_buy(
        self, date: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top stocks with highest foreign net buy value."""
        try:
            top = get_top_stock()
            df = top.foreign_buy(date=date, limit=limit)
            if df is None or df.empty:
                return []
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching top foreign buy: {e}")
            return []

    def get_top_foreign_sell(
        self, date: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top stocks with highest foreign net sell value."""
        try:
            top = get_top_stock()
            df = top.foreign_sell(date=date, limit=limit)
            if df is None or df.empty:
                return []
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching top foreign sell: {e}")
            return []

    def get_top_gainer(
        self, index: str = "VNINDEX", limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top gaining stocks."""
        try:
            top = get_top_stock()
            df = top.gainer(index=index, limit=limit)
            if df is None or df.empty:
                return []
            return self._clean_top_stock_data(df)
        except Exception as e:
            logger.error(f"Error fetching top gainer: {e}")
            return []

    def get_top_loser(
        self, index: str = "VNINDEX", limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top losing stocks."""
        try:
            top = get_top_stock()
            df = top.loser(index=index, limit=limit)
            if df is None or df.empty:
                return []
            return self._clean_top_stock_data(df)
        except Exception as e:
            logger.error(f"Error fetching top loser: {e}")
            return []

    def get_top_value(
        self, index: str = "VNINDEX", limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top stocks by trading value."""
        try:
            top = get_top_stock()
            df = top.value(index=index, limit=limit)
            if df is None or df.empty:
                return []
            return self._clean_top_stock_data(df)
        except Exception as e:
            logger.error(f"Error fetching top value: {e}")
            return []

    def get_top_volume(
        self, index: str = "VNINDEX", limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top stocks by abnormal volume."""
        try:
            top = get_top_stock()
            df = top.volume(index=index, limit=limit)
            if df is None or df.empty:
                return []
            return self._clean_top_stock_data(df)
        except Exception as e:
            logger.error(f"Error fetching top volume: {e}")
            return []

    def get_top_deal(
        self, index: str = "VNINDEX", limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top stocks by block deal volume."""
        try:
            top = get_top_stock()
            df = top.deal(index=index, limit=limit)
            if df is None or df.empty:
                return []
            return self._clean_top_stock_data(df)
        except Exception as e:
            logger.error(f"Error fetching top deal: {e}")
            return []

    def _clean_top_stock_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Clean and simplify top stock data."""
        key_cols = [
            "symbol", "last_price", "price_change_1d", "price_change_pct_1d",
            "accumulated_value", "avg_volume_20d", "volume_spike_20d_pct",
        ]
        available_cols = [c for c in key_cols if c in df.columns]
        if available_cols:
            df = df[available_cols]
        return df.to_dict(orient="records")


class VnstockTradingInsightProvider:
    """Provider for trading insight data (proprietary, foreign) per symbol."""

    def get_proprietary_trading(
        self,
        symbol: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 30,
    ) -> List[Dict[str, Any]]:
        """Get proprietary trading history for a symbol."""
        try:
            trading = get_trading_explorer(symbol)
            df = trading.prop_trade(start=start, end=end, limit=limit)

            if df is None or df.empty:
                return []

            result = []
            for _, row in df.iterrows():
                item = {
                    "trading_date": (
                        row.get("trading_date").isoformat()
                        if pd.notna(row.get("trading_date"))
                        else None
                    ),
                    "buy_volume": self._safe_float(row.get("total_buy_trade_volume")),
                    "buy_value": self._safe_float(row.get("total_buy_trade_value")),
                    "sell_volume": self._safe_float(row.get("total_sell_trade_volume")),
                    "sell_value": self._safe_float(row.get("total_sell_trade_value")),
                    "net_volume": self._safe_float(row.get("total_trade_net_volume")),
                    "net_value": self._safe_float(row.get("total_trade_net_value")),
                    "total_volume": self._safe_float(row.get("total_volume")),
                    "total_value": self._safe_float(row.get("total_value")),
                }
                result.append(item)
            return result
        except Exception as e:
            logger.error(f"Error fetching proprietary trading for {symbol}: {e}")
            return []

    def get_foreign_trading(
        self,
        symbol: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 30,
    ) -> List[Dict[str, Any]]:
        """Get foreign trading history for a symbol."""
        try:
            trading = get_trading_explorer(symbol)
            df = trading.foreign_trade(start=start, end=end, limit=limit)

            if df is None or df.empty:
                return []

            result = []
            for _, row in df.iterrows():
                item = {
                    "trading_date": (
                        row.get("trading_date").isoformat()
                        if pd.notna(row.get("trading_date"))
                        else None
                    ),
                    "buy_volume": self._safe_float(row.get("fr_buy_volume_total")),
                    "buy_value": self._safe_float(row.get("fr_buy_value_total")),
                    "sell_volume": self._safe_float(row.get("fr_sell_volume_total")),
                    "sell_value": self._safe_float(row.get("fr_sell_value_total")),
                    "net_volume": self._safe_float(row.get("fr_net_volume_total")),
                    "net_value": self._safe_float(row.get("fr_net_value_total")),
                    "total_room": self._safe_float(row.get("fr_total_room")),
                    "current_room": self._safe_float(row.get("fr_current_room")),
                    "owned_percent": self._safe_float(row.get("fr_owned_percentage")),
                }
                result.append(item)
            return result
        except Exception as e:
            logger.error(f"Error fetching foreign trading for {symbol}: {e}")
            return []

    def get_order_stats(self, symbol: str) -> List[Dict[str, Any]]:
        """Get order statistics (count/volume by type)."""
        try:
            trading = get_trading_explorer(symbol)
            df = trading.order_stats(to_df=True)
            if df is None or df.empty:
                return []
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching order stats for {symbol}: {e}")
            return []

    def get_side_stats(self, symbol: str) -> List[Dict[str, Any]]:
        """Get side statistics (Buy/Sell volume)."""
        try:
            trading = get_trading_explorer(symbol)
            df = trading.side_stats(to_df=True)
            if df is None or df.empty:
                return []
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching side stats for {symbol}: {e}")
            return []

    def get_insider_trading(
        self,
        symbol: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 30,
    ) -> List[Dict[str, Any]]:
        """Get insider trading history for a symbol."""
        try:
            # Note: insider_deal is from vnstock_data.api.trading.Trading, not explorer
            # Need to use the API Trading class instead
            trading_api = get_trading(symbol)
            df = trading_api.insider_deal(limit=limit)

            if df is None or df.empty:
                return []

            result = []
            for _, row in df.iterrows():
                item = {
                    "start_date": row.get("start_date").isoformat() if pd.notna(row.get("start_date")) else None,
                    "end_date": row.get("end_date").isoformat() if pd.notna(row.get("end_date")) else None,
                    "public_date": row.get("public_date").isoformat() if pd.notna(row.get("public_date")) else None,
                    "share_before_trade": self._safe_float(row.get("share_before_trade")),
                    "share_after_trade": self._safe_float(row.get("share_after_trade")),
                    "share_register": self._safe_float(row.get("share_register")),
                    "share_acquire": self._safe_float(row.get("share_acquire")),
                    "ownership_after_trade": self._safe_float(row.get("ownership_after_trade")),
                    "trader_organ_name": row.get("trader_organ_name"),
                    "action_type": row.get("action_type"),
                    "trade_status": row.get("trade_status"),
                }
                result.append(item)
            return result
        except Exception as e:
            logger.error(f"Error fetching insider trading for {symbol}: {e}")
            return []

    @staticmethod
    def _safe_float(value) -> Optional[float]:
        if value is None or pd.isna(value):
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

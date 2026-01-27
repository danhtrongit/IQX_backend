"""Vnstock quote data provider implementation using vnstock_data."""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import pandas as pd

from app.core.logging import get_logger
from app.infrastructure.vnstock.instance_cache import get_quote, get_trading

logger = get_logger(__name__)


class VnstockQuoteProvider:
    """Provider for vnstock_data quote data."""
    
    def __init__(self, source: str = "vci"):
        self.source = source.lower()
    
    def get_history(
        self,
        symbol: str,
        start: str,
        end: Optional[str],
        interval: str,
        count_back: Optional[int],
    ) -> List[dict]:
        """Get historical OHLCV data."""
        try:
            quote = get_quote(symbol, self.source)
            df = quote.history(
                start=start,
                end=end,
                interval=interval,
                count_back=count_back,
                to_df=True,
            )
            
            if df is None or df.empty:
                return []
            
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching history for {symbol}: {e}")
            return []
    
    def get_intraday(
        self,
        symbol: str,
        page_size: int,
        last_time: Optional[str],
    ) -> List[dict]:
        """Get intraday trades."""
        try:
            quote = get_quote(symbol, self.source)
            df = quote.intraday(
                page_size=page_size,
                last_time=last_time,
                to_df=True,
            )
            
            if df is None or df.empty:
                return []
            
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching intraday for {symbol}: {e}")
            return []
    
    def get_price_board(self, symbols: List[str]) -> List[dict]:
        """Get price board for multiple symbols."""
        if not symbols:
            return []
        
        try:
            trading = get_trading(symbols[0], self.source)
            df = trading.price_board(
                symbols_list=symbols,
                to_df=True,
                flatten_columns=True,
            )
            
            if df is None or df.empty:
                return self._get_price_from_history(symbols)
            
            # Map columns to our schema
            result = []
            for _, row in df.iterrows():
                item = {
                    "symbol": self._get_col(row, ["listing_symbol", "symbol"]),
                    "exchange": self._get_col(row, ["listing_exchange", "exchange"]),
                    "organ_name": self._get_col(row, ["listing_organ_name", "organ_name"]),
                    "price": self._get_col(row, ["match_match_price", "match_price", "price"]),
                    "change": self._get_col(row, ["match_price_change", "change"]),
                    "change_percent": self._get_col(row, ["match_percent_price_change", "change_percent"]),
                    "volume": self._get_col(row, ["match_accumulated_volume", "match_total_volume", "volume"]),
                    "value": self._get_col(row, ["match_accumulated_value", "match_total_value", "value"]),
                    "ref_price": self._get_col(row, ["listing_ref_price", "match_reference_price", "listing_reference_price", "ref_price"]),
                    "ceiling": self._get_col(row, ["listing_ceiling", "match_ceiling_price", "listing_ceiling_price", "ceiling"]),
                    "floor": self._get_col(row, ["listing_floor", "match_floor_price", "listing_floor_price", "floor"]),
                    "open": self._get_col(row, ["match_open_price", "open"]),
                    "high": self._get_col(row, ["match_highest", "match_highest_price", "high"]),
                    "low": self._get_col(row, ["match_lowest", "match_lowest_price", "low"]),
                    "bid_1_price": self._get_col(row, ["bid_ask_bid_1_price"]),
                    "bid_1_volume": self._get_col(row, ["bid_ask_bid_1_volume"]),
                    "bid_2_price": self._get_col(row, ["bid_ask_bid_2_price"]),
                    "bid_2_volume": self._get_col(row, ["bid_ask_bid_2_volume"]),
                    "bid_3_price": self._get_col(row, ["bid_ask_bid_3_price"]),
                    "bid_3_volume": self._get_col(row, ["bid_ask_bid_3_volume"]),
                    "ask_1_price": self._get_col(row, ["bid_ask_ask_1_price"]),
                    "ask_1_volume": self._get_col(row, ["bid_ask_ask_1_volume"]),
                    "ask_2_price": self._get_col(row, ["bid_ask_ask_2_price"]),
                    "ask_2_volume": self._get_col(row, ["bid_ask_ask_2_volume"]),
                    "ask_3_price": self._get_col(row, ["bid_ask_ask_3_price"]),
                    "ask_3_volume": self._get_col(row, ["bid_ask_ask_3_volume"]),
                    "foreign_buy_volume": self._get_col(row, ["match_foreign_buy_volume"]),
                    "foreign_sell_volume": self._get_col(row, ["match_foreign_sell_volume"]),
                }

                # Calculate change/change_percent if not provided
                price = item.get("price")
                ref_price = item.get("ref_price")
                if price is not None and ref_price is not None and ref_price > 0:
                    if item.get("change") is None:
                        item["change"] = round(price - ref_price, 2)
                    if item.get("change_percent") is None:
                        item["change_percent"] = round((price - ref_price) / ref_price * 100, 2)

                result.append(item)
            
            return result
        except Exception as e:
            logger.error(f"Error fetching price board: {e}")
            return self._get_price_from_history(symbols)
    
    def _get_price_from_history(self, symbols: List[str]) -> List[dict]:
        """Fallback: get last close price from history when price_board is empty."""
        result = []
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        
        for symbol in symbols:
            try:
                quote = get_quote(symbol, self.source)
                df = quote.history(
                    start=start_date,
                    end=end_date,
                    interval="1D",
                    to_df=True,
                )
                
                if df is not None and not df.empty:
                    last_row = df.iloc[-1]
                    prev_close = df.iloc[-2]["close"] if len(df) > 1 else last_row.get("close", 0)
                    close_price = float(last_row.get("close", 0))
                    change = close_price - float(prev_close) if prev_close else 0
                    change_pct = (change / float(prev_close) * 100) if prev_close else 0
                    
                    result.append({
                        "symbol": symbol,
                        "exchange": None,
                        "organ_name": None,
                        "price": close_price,
                        "change": round(change, 2),
                        "change_percent": round(change_pct, 2),
                        "volume": int(last_row.get("volume", 0)),
                        "value": None,
                        "ref_price": float(prev_close) if prev_close else None,
                        "ceiling": None,
                        "floor": None,
                        "open": float(last_row.get("open", 0)),
                        "high": float(last_row.get("high", 0)),
                        "low": float(last_row.get("low", 0)),
                        "bid_1_price": None, "bid_1_volume": None,
                        "bid_2_price": None, "bid_2_volume": None,
                        "bid_3_price": None, "bid_3_volume": None,
                        "ask_1_price": None, "ask_1_volume": None,
                        "ask_2_price": None, "ask_2_volume": None,
                        "ask_3_price": None, "ask_3_volume": None,
                        "foreign_buy_volume": None,
                        "foreign_sell_volume": None,
                    })
            except Exception as e:
                logger.warning(f"Error fetching history fallback for {symbol}: {e}")
        
        return result
    
    def get_price_depth(self, symbol: str) -> List[dict]:
        """Get price depth."""
        try:
            quote = get_quote(symbol, self.source)
            df = quote.price_depth(to_df=True)
            
            if df is None or df.empty:
                return []
            
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching price depth for {symbol}: {e}")
            return []
    
    def get_trading_stats(
        self,
        symbol: str,
        resolution: str,
        start: Optional[str],
        end: Optional[str],
        limit: int,
    ) -> List[dict]:
        """Get trading statistics."""
        try:
            trading = get_trading(symbol, self.source)
            df = trading.price_history(
                resolution=resolution,
                start=start,
                end=end,
                limit=limit,
                get_all=False,
            )
            
            if df is None or df.empty:
                return []
            
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error fetching trading stats for {symbol}: {e}")
            return []
    
    @staticmethod
    def _get_col(row, col_names: List[str]):
        """Get column value from row, trying multiple column names."""
        for col in col_names:
            if col in row.index:
                val = row[col]
                if pd.notna(val):
                    return val
        return None

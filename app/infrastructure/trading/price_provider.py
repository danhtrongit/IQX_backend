"""Market price provider implementation."""
from decimal import Decimal
from typing import Optional
from datetime import datetime, time

from app.core.logging import get_logger
from app.application.trading.services import MarketPriceProvider
from app.infrastructure.vnstock.quote_provider import VnstockQuoteProvider

logger = get_logger(__name__)


def is_trading_hours() -> bool:
    """Check if current time is within trading hours (Vietnam timezone)."""
    # Trading hours: 9:00 - 11:30, 13:00 - 15:00 (Vietnam time, UTC+7)
    now = datetime.utcnow()
    # Convert to Vietnam time
    vn_hour = (now.hour + 7) % 24
    vn_time = time(vn_hour, now.minute)
    
    morning_start = time(9, 0)
    morning_end = time(11, 30)
    afternoon_start = time(13, 0)
    afternoon_end = time(15, 0)
    
    # Check weekday (0=Monday, 6=Sunday)
    if now.weekday() >= 5:  # Saturday or Sunday
        return False
    
    return (morning_start <= vn_time <= morning_end) or (afternoon_start <= vn_time <= afternoon_end)


class VnstockMarketPriceProvider(MarketPriceProvider):
    """Market price provider using vnstock API."""
    
    def __init__(self):
        self.quote_provider = VnstockQuoteProvider()
        self._cache: dict[str, tuple[Decimal, datetime]] = {}
        self._cache_ttl = 60  # seconds
    
    async def get_price(self, symbol: str) -> Optional[Decimal]:
        """
        Get current market price for symbol.
        
        During trading hours: use realtime price from price_board
        Outside trading hours: use closing price from history
        """
        symbol = symbol.upper()
        
        # Check cache
        if symbol in self._cache:
            price, cached_at = self._cache[symbol]
            if (datetime.utcnow() - cached_at).seconds < self._cache_ttl:
                return price
        
        try:
            if is_trading_hours():
                price = await self._get_realtime_price(symbol)
            else:
                price = await self._get_closing_price(symbol)
            
            if price:
                self._cache[symbol] = (price, datetime.utcnow())
            
            return price
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            # Try to return cached price even if expired
            if symbol in self._cache:
                return self._cache[symbol][0]
            return None
    
    async def _get_realtime_price(self, symbol: str) -> Optional[Decimal]:
        """Get realtime price from price board."""
        try:
            data = self.quote_provider.get_price_board([symbol])
            if data and len(data) > 0:
                price = data[0].get("price")
                if price:
                    return Decimal(str(price))
        except Exception as e:
            logger.error(f"Error getting realtime price for {symbol}: {e}")
        
        # Fallback to closing price
        return await self._get_closing_price(symbol)
    
    async def _get_closing_price(self, symbol: str) -> Optional[Decimal]:
        """Get closing price from history."""
        try:
            from datetime import timedelta
            end_date = datetime.utcnow().strftime("%Y-%m-%d")
            start_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            data = self.quote_provider.get_history(
                symbol=symbol,
                start=start_date,
                end=end_date,
                interval="1D",
                count_back=1,
            )
            
            if data and len(data) > 0:
                # Get the most recent close price
                close = data[-1].get("close")
                if close:
                    return Decimal(str(close))
        except Exception as e:
            logger.error(f"Error getting closing price for {symbol}: {e}")
        
        return None
    
    def clear_cache(self):
        """Clear price cache."""
        self._cache.clear()

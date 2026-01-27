"""
Cached vnstock instances to avoid repeated initialization overhead.

vnstock classes have initialization overhead (HTTP setup, validation, etc.)
Caching instances significantly improves performance for repeated calls.
"""
from typing import Dict, Any, Optional
from threading import Lock

# Thread-safe caches for vnstock instances
_quote_cache: Dict[str, Any] = {}
_trading_cache: Dict[str, Any] = {}
_trading_explorer_cache: Dict[str, Any] = {}  # For vnstock_data.explorer.vci.trading
_company_cache: Dict[str, Any] = {}
_finance_cache: Dict[str, Any] = {}
_listing_cache: Dict[str, Any] = {}
_market_cache: Dict[str, Any] = {}
_top_stock_cache: Dict[str, Any] = {}
_macro_cache: Dict[str, Any] = {}
_commodity_cache: Dict[str, Any] = {}

_lock = Lock()


def get_quote(symbol: str, source: str = "vci"):
    """Get cached Quote instance."""
    key = f"{source}:{symbol.upper()}"
    if key not in _quote_cache:
        with _lock:
            if key not in _quote_cache:
                from vnstock import Quote
                _quote_cache[key] = Quote(source=source, symbol=symbol.upper(), show_log=False)
    return _quote_cache[key]


def get_trading(symbol: str = "", source: str = "vci"):
    """Get cached Trading instance."""
    key = f"{source}:{symbol.upper() or 'default'}"
    if key not in _trading_cache:
        with _lock:
            if key not in _trading_cache:
                from vnstock import Trading
                _trading_cache[key] = Trading(
                    source=source, 
                    symbol=symbol.upper() or "VCI", 
                    show_log=False
                )
    return _trading_cache[key]


def get_company(symbol: str, source: str = "vci"):
    """Get cached Company instance."""
    key = f"{source}:{symbol.upper()}"
    if key not in _company_cache:
        with _lock:
            if key not in _company_cache:
                from vnstock import Company
                _company_cache[key] = Company(source=source, symbol=symbol.upper(), show_log=False)
    return _company_cache[key]


def get_finance(symbol: str, period: str = "quarter", source: str = "vci"):
    """Get cached Finance instance."""
    key = f"{source}:{symbol.upper()}:{period}"
    if key not in _finance_cache:
        with _lock:
            if key not in _finance_cache:
                from vnstock import Finance
                _finance_cache[key] = Finance(
                    source=source,
                    symbol=symbol.upper(),
                    period=period,
                    get_all=True,
                    show_log=False,
                )
    return _finance_cache[key]


def get_listing(source: str = "vci"):
    """Get cached Listing instance."""
    if source not in _listing_cache:
        with _lock:
            if source not in _listing_cache:
                from vnstock import Listing
                _listing_cache[source] = Listing(source=source, show_log=False)
    return _listing_cache[source]


def get_market(source: str = "vnd"):
    """Get cached Market instance."""
    if source not in _market_cache:
        with _lock:
            if source not in _market_cache:
                from vnstock import Market
                _market_cache[source] = Market(source=source, show_log=False)
    return _market_cache[source]


def get_top_stock(source: str = "vnd"):
    """Get cached TopStock instance."""
    if source not in _top_stock_cache:
        with _lock:
            if source not in _top_stock_cache:
                from vnstock import TopStock
                _top_stock_cache[source] = TopStock(source=source)
    return _top_stock_cache[source]


def get_macro(source: str = "mbk"):
    """Get cached Macro instance."""
    if source not in _macro_cache:
        with _lock:
            if source not in _macro_cache:
                from vnstock import Macro
                _macro_cache[source] = Macro(source=source, show_log=False)
    return _macro_cache[source]


def get_commodity(source: str = "spl"):
    """Get cached CommodityPrice instance."""
    if source not in _commodity_cache:
        with _lock:
            if source not in _commodity_cache:
                from vnstock import CommodityPrice
                _commodity_cache[source] = CommodityPrice(source=source, show_log=False)
    return _commodity_cache[source]


def get_trading_explorer(symbol: str):
    """Get cached Trading instance from vnstock.explorer.vci.trading."""
    key = symbol.upper()
    if key not in _trading_explorer_cache:
        with _lock:
            if key not in _trading_explorer_cache:
                from vnstock.explorer.vci.trading import Trading
                _trading_explorer_cache[key] = Trading(symbol=key, show_log=False)
    return _trading_explorer_cache[key]


def clear_cache():
    """Clear all cached instances (useful for testing)."""
    with _lock:
        _quote_cache.clear()
        _trading_cache.clear()
        _trading_explorer_cache.clear()
        _company_cache.clear()
        _finance_cache.clear()
        _listing_cache.clear()
        _market_cache.clear()
        _top_stock_cache.clear()
        _macro_cache.clear()
        _commodity_cache.clear()

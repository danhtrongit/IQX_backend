"""Price streaming service using python-socketio client."""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Set, Optional, Callable, List

import socketio

from app.core.logging import get_logger

logger = get_logger(__name__)

# VPS WebSocket URL
VPS_WS_URL = "wss://bgdatafeed.vps.com.vn"


class PriceData:
    """Parsed price data."""

    def __init__(self, raw_data: Dict[str, Any]):
        self.symbol: str = raw_data.get("symbol", "")
        self.last_price: Optional[float] = self._safe_float(raw_data.get("lastPrice"))
        self.last_volume: Optional[int] = self._safe_int(raw_data.get("lastVol"))
        self.change: Optional[float] = self._safe_float(raw_data.get("change"))
        self.change_percent: Optional[float] = self._safe_float(raw_data.get("changePc"))
        self.total_volume: Optional[int] = self._safe_int(raw_data.get("totalVol"))
        self.high_price: Optional[float] = self._safe_float(raw_data.get("hp"))
        self.low_price: Optional[float] = self._safe_float(raw_data.get("lp"))
        self.open_price: Optional[float] = self._safe_float(raw_data.get("openPrice"))
        self.average_price: Optional[float] = self._safe_float(raw_data.get("ap"))
        self.reference_price: Optional[float] = self._safe_float(raw_data.get("r"))
        self.ceiling_price: Optional[float] = self._safe_float(raw_data.get("c"))
        self.floor_price: Optional[float] = self._safe_float(raw_data.get("f"))
        self.side: Optional[str] = raw_data.get("side")
        self.timestamp: float = datetime.now().timestamp()
        self.event_type: str = "stock"

    @staticmethod
    def _safe_float(val) -> Optional[float]:
        if val is None:
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _safe_int(val) -> Optional[int]:
        if val is None:
            return None
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "last_price": self.last_price,
            "last_volume": self.last_volume,
            "change": self.change,
            "change_percent": self.change_percent,
            "total_volume": self.total_volume,
            "high_price": self.high_price,
            "low_price": self.low_price,
            "open_price": self.open_price,
            "average_price": self.average_price,
            "reference_price": self.reference_price,
            "ceiling_price": self.ceiling_price,
            "floor_price": self.floor_price,
            "side": self.side,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
        }


class IndexData:
    """Parsed index data."""

    def __init__(self, raw_data: Dict[str, Any]):
        self.index_id: str = raw_data.get("index_id", "") or raw_data.get("mc", "")
        self.market_code: str = raw_data.get("mc", "")
        self.exchange: str = raw_data.get("exchange", "")
        self.current_index: Optional[float] = self._safe_float(raw_data.get("cIndex"))
        self.open_index: Optional[float] = self._safe_float(raw_data.get("oIndex"))
        self.change: Optional[float] = None
        self.percent_change: Optional[float] = None
        self.volume: Optional[int] = self._safe_int(raw_data.get("vol"))
        self.value: Optional[float] = self._safe_float(raw_data.get("value"))
        self.advances: Optional[int] = None
        self.declines: Optional[int] = None
        self.unchanged: Optional[int] = None
        self.timestamp: float = datetime.now().timestamp()
        
        # Parse 'ot' field: "change|percent|value|advances|declines|unchanged"
        ot = raw_data.get("ot", "")
        if ot:
            parts = ot.split("|")
            if len(parts) >= 6:
                self.change = self._safe_float(parts[0])
                pct = parts[1].replace("%", "") if parts[1] else None
                self.percent_change = self._safe_float(pct)
                self.advances = self._safe_int(parts[3])
                self.declines = self._safe_int(parts[4])
                self.unchanged = self._safe_int(parts[5])

    @staticmethod
    def _safe_float(val) -> Optional[float]:
        if val is None:
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _safe_int(val) -> Optional[int]:
        if val is None:
            return None
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index_id": self.index_id,
            "market_code": self.market_code,
            "exchange": self.exchange,
            "current_index": self.current_index,
            "open_index": self.open_index,
            "change": self.change,
            "percent_change": self.percent_change,
            "volume": self.volume,
            "value": self.value,
            "advances": self.advances,
            "declines": self.declines,
            "unchanged": self.unchanged,
            "timestamp": self.timestamp,
        }


# Index code mapping (mc -> name, exchange)
INDEX_CODES = {
    "10": ("VNINDEX", "HOSE"),
    "02": ("HNX-INDEX", "HNX"),
    "03": ("UPCOM-INDEX", "UPCOM"),
    "11": ("VN30", "HOSE"),
    "28": ("VN100", "HOSE"),
    "29": ("VNALL", "HOSE"),
    "32": ("HNX30", "HNX"),
    "33": ("HNXLCAP", "HNX"),
    "35": ("HNXSMCAP", "HNX"),
    "37": ("HNXFIN", "HNX"),
    "39": ("HNXMAN", "HNX"),
    "43": ("HNXCON", "HNX"),
    "34": ("HNXMID", "HNX"),
    "36": ("HNXIND", "HNX"),
    "38": ("HNXUT", "HNX"),
    "40": ("HNXREAL", "HNX"),
    "41": ("HNXTECH", "HNX"),
    "42": ("HNXENER", "HNX"),
}


class PriceStreamManager:
    """
    Manages Socket.IO connection to VPS data feed using python-socketio.
    """

    def __init__(self):
        self._sio: Optional[socketio.AsyncClient] = None
        self._running = False
        self._subscribed_symbols: Set[str] = set()
        self._callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self._price_cache: Dict[str, PriceData] = {}
        self._index_cache: Dict[str, IndexData] = {}
        self._lock = asyncio.Lock()
        self._reconnect_count = 0
        self._max_reconnect = 10
        self._market = "HOSE"
        self._message_count = 0

    @property
    def is_connected(self) -> bool:
        return self._sio is not None and self._sio.connected

    @property
    def subscribed_symbols(self) -> Set[str]:
        return self._subscribed_symbols.copy()

    def get_cached_price(self, symbol: str) -> Optional[PriceData]:
        return self._price_cache.get(symbol.upper())

    def get_cached_index(self, index_id: str) -> Optional[IndexData]:
        return self._index_cache.get(index_id)

    def get_all_cached_prices(self) -> Dict[str, Dict[str, Any]]:
        return {k: v.to_dict() for k, v in self._price_cache.items()}

    def get_all_cached_indices(self) -> Dict[str, Dict[str, Any]]:
        return {k: v.to_dict() for k, v in self._index_cache.items()}

    def add_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    async def _notify_callbacks(self, data: Dict[str, Any]) -> None:
        for callback in self._callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"Callback error: {e}")

    def _process_stock_data(self, data: Dict[str, Any]) -> Optional[PriceData]:
        """Process stock data from event."""
        # Handle nested data structure
        if "data" in data:
            data = data["data"]

        symbol = data.get("sym") or data.get("symbol")
        if not symbol:
            return None

        mapped = {
            "symbol": symbol,
            "lastPrice": data.get("lastPrice"),
            "lastVol": data.get("lastVol") or data.get("lv"),
            "change": data.get("change"),
            "changePc": data.get("changePc"),
            "totalVol": data.get("totalVol"),
            "hp": data.get("hp"),
            "lp": data.get("lp"),
            "openPrice": data.get("openPrice"),
            "ap": data.get("ap"),
            "r": data.get("r"),
            "c": data.get("c"),
            "f": data.get("f"),
            "side": data.get("side"),
        }
        return PriceData(mapped)

    def _process_index_data(self, data: Dict[str, Any]) -> Optional[IndexData]:
        """Process index data from event."""
        if "data" in data:
            data = data["data"]

        mc = data.get("mc")
        if not mc:
            return None

        # Map index code to name and exchange
        index_info = INDEX_CODES.get(mc)
        if index_info:
            index_name, exchange = index_info
        else:
            index_name = mc
            exchange = "UNKNOWN"
        
        data["index_id"] = index_name
        data["exchange"] = exchange

        return IndexData(data)

    async def _setup_event_handlers(self) -> None:
        """Setup Socket.IO event handlers."""

        @self._sio.event
        async def connect():
            logger.info("Socket.IO connected")
            self._reconnect_count = 0
            # Send subscription after connect
            await self._send_subscriptions()

        @self._sio.event
        async def disconnect():
            logger.warning("Socket.IO disconnected")

        @self._sio.on("stock")
        async def on_stock(data):
            self._message_count += 1
            price = self._process_stock_data(data)
            if price and price.symbol:
                symbol_upper = price.symbol.upper()
                # Cache all stocks, filter when sending to callbacks
                self._price_cache[symbol_upper] = price
                # Only notify if subscribed or no subscription filter
                if not self._subscribed_symbols or symbol_upper in self._subscribed_symbols:
                    await self._notify_callbacks({"event_type": "stock", **price.to_dict()})

        @self._sio.on("index")
        async def on_index(data):
            self._message_count += 1
            idx = self._process_index_data(data)
            if idx and idx.index_id:
                self._index_cache[idx.index_id] = idx
                await self._notify_callbacks({"event_type": "index", **idx.to_dict()})

        @self._sio.on("board")
        async def on_board(data):
            self._message_count += 1
            # Board data contains order book info, process as stock update
            if "data" in data:
                d = data["data"]
                symbol = d.get("sym") or d.get("symbol")
                if symbol:
                    # Update existing price data with board info if available
                    pass

        @self._sio.on("stockps")
        async def on_stockps(data):
            self._message_count += 1
            # Derivative/futures data
            pass

        @self._sio.on("regs")
        async def on_regs(data):
            logger.info(f"Subscription confirmed: {data}")

    async def _send_subscriptions(self) -> None:
        """Send subscription message."""
        if not self._sio or not self._sio.connected or not self._subscribed_symbols:
            return

        symbols_str = ",".join(self._subscribed_symbols)
        # Payload must be a JSON string (double-encoded)
        payload = json.dumps({"action": "join", "list": symbols_str})

        try:
            await self._sio.emit("regs", payload)
            logger.info(f"Sent subscription: {payload}")
        except Exception as e:
            logger.error(f"Subscribe error: {e}")

    async def connect(self, market: str = "HOSE") -> None:
        """Connect to VPS Socket.IO server."""
        async with self._lock:
            if self._running:
                logger.warning("Already connected or connecting")
                return

            self._running = True
            self._market = market

            # Create Socket.IO client
            self._sio = socketio.AsyncClient(
                logger=False,
                engineio_logger=False,
                reconnection=True,
                reconnection_attempts=self._max_reconnect,
                reconnection_delay=1,
                reconnection_delay_max=60,
            )

            # Setup event handlers
            await self._setup_event_handlers()

            # Connect in background
            asyncio.create_task(self._do_connect())

    async def _do_connect(self) -> None:
        """Perform actual connection."""
        try:
            logger.info(f"Connecting to {VPS_WS_URL}...")
            await self._sio.connect(
                VPS_WS_URL,
                transports=["websocket"],
                socketio_path="/socket.io/",
            )
            logger.info("Connected to VPS data feed")
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self._running = False

    async def disconnect(self) -> None:
        """Disconnect from Socket.IO server."""
        async with self._lock:
            self._running = False
            if self._sio:
                try:
                    await self._sio.disconnect()
                except Exception as e:
                    logger.error(f"Disconnect error: {e}")
                self._sio = None
            logger.info("Disconnected")

    async def subscribe(self, symbols: List[str]) -> None:
        """Subscribe to symbols."""
        symbols = [s.upper() for s in symbols]
        new_symbols = set(symbols) - self._subscribed_symbols
        self._subscribed_symbols.update(new_symbols)

        if self.is_connected and new_symbols:
            await self._send_subscriptions()

    async def unsubscribe(self, symbols: List[str]) -> None:
        """Unsubscribe from symbols."""
        symbols = [s.upper() for s in symbols]
        self._subscribed_symbols -= set(symbols)
        for symbol in symbols:
            self._price_cache.pop(symbol, None)

    def get_connection_stats(self) -> Dict[str, Any]:
        return {
            "connected": self.is_connected,
            "reconnect_count": self._reconnect_count,
            "message_count": self._message_count,
            "cached_prices": len(self._price_cache),
            "cached_indices": len(self._index_cache),
            "subscribed_symbols": list(self._subscribed_symbols),
        }


# Global singleton
price_stream_manager = PriceStreamManager()

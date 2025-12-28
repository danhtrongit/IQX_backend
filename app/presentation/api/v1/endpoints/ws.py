"""WebSocket endpoints for realtime data streaming with optimizations."""
import asyncio
import gzip
import json
import time
from collections import defaultdict
from typing import Set, Dict, Any, List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from starlette.websockets import WebSocketState

from app.core.logging import get_logger
from app.infrastructure.streaming.price_stream import price_stream_manager

logger = get_logger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])

# Configuration
MAX_SYMBOLS_PER_CLIENT = 1000  # Maximum symbols a single client can subscribe
BATCH_SIZE = 100  # Send subscriptions in batches
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 30  # max subscribe/unsubscribe per minute
COMPRESSION_THRESHOLD = 1024  # bytes - compress if larger
MAX_CONNECTIONS_PER_IP = 10  # Maximum connections per IP


class RateLimiter:
    """Simple rate limiter for WebSocket actions."""
    
    def __init__(self, window: int = RATE_LIMIT_WINDOW, max_requests: int = RATE_LIMIT_MAX_REQUESTS):
        self.window = window
        self.max_requests = max_requests
        self._requests: Dict[str, List[float]] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed."""
        async with self._lock:
            now = time.time()
            # Clean old requests
            self._requests[client_id] = [
                ts for ts in self._requests[client_id] 
                if now - ts < self.window
            ]
            
            if len(self._requests[client_id]) >= self.max_requests:
                return False
            
            self._requests[client_id].append(now)
            return True
    
    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests in current window."""
        now = time.time()
        valid_requests = [
            ts for ts in self._requests[client_id] 
            if now - ts < self.window
        ]
        return max(0, self.max_requests - len(valid_requests))
    
    def cleanup(self):
        """Clean up expired entries."""
        now = time.time()
        to_delete = []
        for client_id, timestamps in self._requests.items():
            valid = [ts for ts in timestamps if now - ts < self.window]
            if not valid:
                to_delete.append(client_id)
            else:
                self._requests[client_id] = valid
        
        for client_id in to_delete:
            del self._requests[client_id]


class ConnectionPool:
    """Manages WebSocket connection pool with IP limiting."""
    
    def __init__(self, max_per_ip: int = MAX_CONNECTIONS_PER_IP):
        self.max_per_ip = max_per_ip
        self._connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()
    
    async def can_connect(self, ip: str) -> bool:
        """Check if IP can make new connection."""
        async with self._lock:
            return len(self._connections[ip]) < self.max_per_ip
    
    async def add(self, ip: str, websocket: WebSocket) -> bool:
        """Add connection. Returns False if limit exceeded."""
        async with self._lock:
            if len(self._connections[ip]) >= self.max_per_ip:
                return False
            self._connections[ip].add(websocket)
            return True
    
    async def remove(self, ip: str, websocket: WebSocket):
        """Remove connection."""
        async with self._lock:
            self._connections[ip].discard(websocket)
            if not self._connections[ip]:
                del self._connections[ip]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        return {
            "total_connections": sum(len(v) for v in self._connections.values()),
            "unique_ips": len(self._connections),
            "connections_by_ip": {ip: len(conns) for ip, conns in self._connections.items()},
        }


class ConnectionManager:
    """Manages WebSocket connections with optimizations."""
    
    def __init__(self):
        self.active_connections: Dict[WebSocket, Set[str]] = {}
        self._client_info: Dict[WebSocket, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self._stream_callback_registered = False
        
        # Optimizations
        self.rate_limiter = RateLimiter()
        self.connection_pool = ConnectionPool()
        
        # Message batching for broadcasts
        self._pending_messages: Dict[WebSocket, List[Dict[str, Any]]] = defaultdict(list)
        self._batch_task: Optional[asyncio.Task] = None
        
        # Compression settings
        self.compression_enabled = True
        self.compression_threshold = COMPRESSION_THRESHOLD
    
    def _get_client_ip(self, websocket: WebSocket) -> str:
        """Get client IP from WebSocket."""
        if websocket.client:
            return websocket.client.host
        return "unknown"
    
    def _get_client_id(self, websocket: WebSocket) -> str:
        """Get unique client ID."""
        return f"{self._get_client_ip(websocket)}:{id(websocket)}"
    
    async def connect(
        self, 
        websocket: WebSocket, 
        symbols: List[str] = None,
        enable_compression: bool = True,
    ) -> bool:
        """Accept a new WebSocket connection. Returns False if rejected."""
        client_ip = self._get_client_ip(websocket)
        
        # Check connection pool limit
        if not await self.connection_pool.can_connect(client_ip):
            logger.warning(f"Connection limit exceeded for IP: {client_ip}")
            await websocket.close(code=1008, reason="Connection limit exceeded")
            return False
        
        await websocket.accept()
        
        async with self._lock:
            # Add to connection pool
            await self.connection_pool.add(client_ip, websocket)
            
            # Initialize connection
            self.active_connections[websocket] = set()
            self._client_info[websocket] = {
                "ip": client_ip,
                "connected_at": time.time(),
                "compression": enable_compression,
                "messages_sent": 0,
                "bytes_sent": 0,
            }
            
            # Auto-connect stream if not connected
            if not price_stream_manager.is_connected:
                try:
                    await price_stream_manager.connect(market="HOSE")
                    logger.info("Auto-connected price stream")
                except Exception as e:
                    logger.warning(f"Failed to auto-connect stream: {e}")
            
            # Subscribe to initial symbols with batching
            if symbols:
                await self._subscribe_with_batching(websocket, symbols)
            
            # Register callback if not already done
            if not self._stream_callback_registered:
                price_stream_manager.add_callback(self._on_price_update)
                self._stream_callback_registered = True
        
        logger.info(f"WebSocket connected from {client_ip}. Total: {len(self.active_connections)}")
        return True
    
    async def disconnect(self, websocket: WebSocket) -> None:
        """Handle WebSocket disconnection."""
        async with self._lock:
            if websocket in self.active_connections:
                del self.active_connections[websocket]
            
            if websocket in self._client_info:
                client_ip = self._client_info[websocket]["ip"]
                await self.connection_pool.remove(client_ip, websocket)
                del self._client_info[websocket]
            
            if websocket in self._pending_messages:
                del self._pending_messages[websocket]
        
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def _subscribe_with_batching(
        self, 
        websocket: WebSocket, 
        symbols: List[str],
    ) -> None:
        """Subscribe to symbols with batching."""
        symbols = [s.upper() for s in symbols[:MAX_SYMBOLS_PER_CLIENT]]
        
        if websocket in self.active_connections:
            self.active_connections[websocket].update(symbols)
        
        # Batch subscriptions to price stream
        for i in range(0, len(symbols), BATCH_SIZE):
            batch = symbols[i:i + BATCH_SIZE]
            await price_stream_manager.subscribe(batch)
            
            # Small delay between batches to avoid overwhelming the stream
            if i + BATCH_SIZE < len(symbols):
                await asyncio.sleep(0.05)
    
    async def subscribe(
        self, 
        websocket: WebSocket, 
        symbols: List[str],
    ) -> Dict[str, Any]:
        """Subscribe with rate limiting and batching."""
        client_id = self._get_client_id(websocket)
        
        # Rate limiting
        if not await self.rate_limiter.is_allowed(client_id):
            remaining = self.rate_limiter.get_remaining(client_id)
            return {
                "success": False,
                "error": "Rate limit exceeded",
                "retry_after": RATE_LIMIT_WINDOW,
                "remaining": remaining,
            }
        
        # Limit total symbols per client
        current = len(self.active_connections.get(websocket, set()))
        available = MAX_SYMBOLS_PER_CLIENT - current
        
        if available <= 0:
            return {
                "success": False,
                "error": f"Maximum symbols limit ({MAX_SYMBOLS_PER_CLIENT}) reached",
                "current": current,
            }
        
        # Take only what we can
        symbols = symbols[:available]
        
        # Subscribe with batching
        await self._subscribe_with_batching(websocket, symbols)
        
        # Send cached prices for new symbols
        await self._send_cached_prices(websocket, symbols)
        
        return {
            "success": True,
            "subscribed": len(symbols),
            "total": len(self.active_connections.get(websocket, set())),
            "remaining_quota": MAX_SYMBOLS_PER_CLIENT - len(self.active_connections.get(websocket, set())),
        }
    
    async def unsubscribe(
        self, 
        websocket: WebSocket, 
        symbols: List[str],
    ) -> Dict[str, Any]:
        """Unsubscribe with rate limiting."""
        client_id = self._get_client_id(websocket)
        
        # Rate limiting (less strict for unsubscribe)
        if not await self.rate_limiter.is_allowed(client_id):
            return {
                "success": False,
                "error": "Rate limit exceeded",
            }
        
        symbols = [s.upper() for s in symbols]
        
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections[websocket] -= set(symbols)
        
        return {
            "success": True,
            "unsubscribed": len(symbols),
            "remaining": len(self.active_connections.get(websocket, set())),
        }
    
    async def _send_cached_prices(self, websocket: WebSocket, symbols: List[str]) -> None:
        """Send cached prices for subscribed symbols."""
        cached_data = {}
        for symbol in symbols:
            cached = price_stream_manager.get_cached_price(symbol.upper())
            if cached:
                cached_data[symbol.upper()] = cached.to_dict()
        
        if cached_data:
            await self._send_to_websocket(websocket, {
                "type": "cached_prices",
                "data": cached_data,
                "count": len(cached_data),
            })
    
    async def _on_price_update(self, data: Dict[str, Any]) -> None:
        """Handle price update from stream."""
        event_type = data.get("event_type", "")
        symbol = data.get("symbol", "")
        
        if event_type == "stock" and symbol:
            message = {"type": "price", "data": data}
            await self._broadcast_to_symbol(symbol, message)
        elif event_type == "index":
            message = {"type": "index", "data": data}
            await self._broadcast_all(message)
    
    async def _broadcast_to_symbol(self, symbol: str, message: Dict[str, Any]) -> None:
        """Broadcast message to connections subscribed to a symbol."""
        symbol = symbol.upper()
        disconnected = []
        
        for websocket, subscribed_symbols in list(self.active_connections.items()):
            if symbol in subscribed_symbols or "*" in subscribed_symbols:
                success = await self._send_to_websocket(websocket, message)
                if not success:
                    disconnected.append(websocket)
        
        for ws in disconnected:
            await self.disconnect(ws)
    
    async def _broadcast_all(self, message: Dict[str, Any]) -> None:
        """Broadcast message to all connections."""
        disconnected = []
        
        for websocket in list(self.active_connections.keys()):
            success = await self._send_to_websocket(websocket, message)
            if not success:
                disconnected.append(websocket)
        
        for ws in disconnected:
            await self.disconnect(ws)
    
    async def _send_to_websocket(
        self, 
        websocket: WebSocket, 
        message: Dict[str, Any],
    ) -> bool:
        """Send message to a WebSocket with optional compression."""
        try:
            if websocket.client_state != WebSocketState.CONNECTED:
                return False
            
            # Serialize message
            json_data = json.dumps(message)
            data_bytes = json_data.encode('utf-8')
            
            client_info = self._client_info.get(websocket, {})
            use_compression = (
                client_info.get("compression", True) and 
                len(data_bytes) > self.compression_threshold
            )
            
            if use_compression:
                # Compress and send as binary
                compressed = gzip.compress(data_bytes)
                # Only use compression if it actually reduces size
                if len(compressed) < len(data_bytes):
                    await websocket.send_bytes(compressed)
                    bytes_sent = len(compressed)
                else:
                    await websocket.send_text(json_data)
                    bytes_sent = len(data_bytes)
            else:
                await websocket.send_text(json_data)
                bytes_sent = len(data_bytes)
            
            # Update stats
            if websocket in self._client_info:
                self._client_info[websocket]["messages_sent"] += 1
                self._client_info[websocket]["bytes_sent"] += bytes_sent
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending to WebSocket: {e}")
            return False
    
    def get_client_stats(self, websocket: WebSocket) -> Optional[Dict[str, Any]]:
        """Get stats for a specific client."""
        if websocket not in self._client_info:
            return None
        
        info = self._client_info[websocket]
        subscribed = self.active_connections.get(websocket, set())
        
        return {
            "ip": info["ip"],
            "connected_duration": time.time() - info["connected_at"],
            "compression_enabled": info["compression"],
            "messages_sent": info["messages_sent"],
            "bytes_sent": info["bytes_sent"],
            "subscribed_count": len(subscribed),
            "rate_limit_remaining": self.rate_limiter.get_remaining(
                self._get_client_id(websocket)
            ),
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get overall connection stats."""
        total_subscriptions = sum(
            len(subs) for subs in self.active_connections.values()
        )
        total_messages = sum(
            info.get("messages_sent", 0) 
            for info in self._client_info.values()
        )
        total_bytes = sum(
            info.get("bytes_sent", 0) 
            for info in self._client_info.values()
        )
        
        return {
            "total_connections": len(self.active_connections),
            "total_subscriptions": total_subscriptions,
            "total_messages_sent": total_messages,
            "total_bytes_sent": total_bytes,
            "pool_stats": self.connection_pool.get_stats(),
            "stream_stats": price_stream_manager.get_connection_stats(),
        }


# Global connection manager
manager = ConnectionManager()


@router.websocket("/prices")
async def websocket_prices(
    websocket: WebSocket,
    symbols: str = Query(None, description="Comma-separated symbols to subscribe"),
    compress: bool = Query(True, description="Enable gzip compression for large messages"),
):
    """
    WebSocket endpoint for realtime price streaming with optimizations.
    
    **Features:**
    - Batched subscriptions for large symbol lists
    - Rate limiting (30 subscribe/unsubscribe per minute)
    - Connection pooling (max 10 connections per IP)
    - Optional gzip compression for large messages
    - Maximum 1000 symbols per client
    
    **Connection:**
    ```
    ws://localhost:8000/api/v1/ws/prices?symbols=VNM,FPT,VCB&compress=true
    ```
    
    **Messages from server:**
    ```json
    {"type": "price", "data": {"symbol": "VNM", "last_price": 75000, ...}}
    {"type": "index", "data": {"index_id": "VNINDEX", "current_index": 1200, ...}}
    {"type": "cached_prices", "data": {...}, "count": 10}
    ```
    
    **Messages to server:**
    ```json
    {"action": "subscribe", "symbols": ["ACB", "TCB"]}
    {"action": "unsubscribe", "symbols": ["VNM"]}
    {"action": "get_cached"}
    {"action": "get_indices"}
    {"action": "get_stats"}
    {"action": "ping"}
    ```
    
    **Compression:**
    - Messages larger than 1KB are gzip compressed
    - Sent as binary WebSocket frames
    - Client must decompress with gunzip
    """
    # Parse initial symbols
    initial_symbols = []
    if symbols:
        initial_symbols = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    
    # Connect with optimizations
    connected = await manager.connect(
        websocket, 
        initial_symbols,
        enable_compression=compress,
    )
    
    if not connected:
        return
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                action = message.get("action", "")
                
                if action == "subscribe":
                    syms = message.get("symbols", [])
                    if syms:
                        result = await manager.subscribe(websocket, syms)
                        await websocket.send_json({
                            "type": "subscribed",
                            **result,
                        })
                
                elif action == "unsubscribe":
                    syms = message.get("symbols", [])
                    if syms:
                        result = await manager.unsubscribe(websocket, syms)
                        await websocket.send_json({
                            "type": "unsubscribed",
                            **result,
                        })
                
                elif action == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": time.time(),
                    })
                
                elif action == "get_cached":
                    subscribed = manager.active_connections.get(websocket, set())
                    cached = {}
                    for sym in subscribed:
                        price = price_stream_manager.get_cached_price(sym)
                        if price:
                            cached[sym] = price.to_dict()
                    await websocket.send_json({
                        "type": "cached_prices",
                        "data": cached,
                        "count": len(cached),
                    })
                
                elif action == "get_indices":
                    indices = price_stream_manager.get_all_cached_indices()
                    await websocket.send_json({
                        "type": "indices",
                        "data": indices,
                        "count": len(indices),
                    })
                
                elif action == "get_stats":
                    stats = manager.get_client_stats(websocket)
                    await websocket.send_json({
                        "type": "stats",
                        "data": stats,
                    })
                
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown action: {action}",
                        "valid_actions": [
                            "subscribe", "unsubscribe", "ping", 
                            "get_cached", "get_indices", "get_stats"
                        ],
                    })
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON",
                })
                
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket)


@router.get("/stream/status")
async def get_stream_status():
    """
    Get price stream and connection status.
    
    Returns comprehensive stats about the WebSocket infrastructure.
    """
    return {
        "stream": {
            "status": "connected" if price_stream_manager.is_connected else "disconnected",
            "stats": price_stream_manager.get_connection_stats(),
        },
        "connections": manager.get_stats(),
        "config": {
            "max_symbols_per_client": MAX_SYMBOLS_PER_CLIENT,
            "batch_size": BATCH_SIZE,
            "rate_limit_window": RATE_LIMIT_WINDOW,
            "rate_limit_max_requests": RATE_LIMIT_MAX_REQUESTS,
            "compression_threshold": COMPRESSION_THRESHOLD,
            "max_connections_per_ip": MAX_CONNECTIONS_PER_IP,
        },
    }


@router.post("/stream/connect")
async def connect_stream(market: str = Query("HOSE", description="Market: HOSE, HNX, UPCOM")):
    """
    Connect to the price stream.
    
    This starts the WebSocket connection to VPS data feed.
    """
    try:
        await price_stream_manager.connect(market=market)
        await asyncio.sleep(0.5)
        
        return {
            "status": "connecting",
            "market": market,
            "stats": price_stream_manager.get_connection_stats(),
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }


@router.post("/stream/disconnect")
async def disconnect_stream():
    """Disconnect from the price stream."""
    await price_stream_manager.disconnect()
    return {"status": "disconnected"}


@router.post("/stream/subscribe")
async def subscribe_symbols(symbols: List[str]):
    """
    Subscribe to symbols for price updates (with batching).
    """
    # Batch subscribe
    subscribed = []
    for i in range(0, len(symbols), BATCH_SIZE):
        batch = symbols[i:i + BATCH_SIZE]
        await price_stream_manager.subscribe(batch)
        subscribed.extend(batch)
        if i + BATCH_SIZE < len(symbols):
            await asyncio.sleep(0.05)
    
    return {
        "subscribed": len(subscribed),
        "total_subscribed": len(price_stream_manager.subscribed_symbols),
    }


@router.get("/stream/prices")
async def get_cached_prices(symbols: str = Query(None, description="Comma-separated symbols")):
    """
    Get cached prices from the stream.
    """
    if symbols:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        result = {}
        for sym in symbol_list:
            cached = price_stream_manager.get_cached_price(sym)
            if cached:
                result[sym] = cached.to_dict()
        return {"prices": result, "count": len(result)}
    
    all_prices = price_stream_manager.get_all_cached_prices()
    return {"prices": all_prices, "count": len(all_prices)}

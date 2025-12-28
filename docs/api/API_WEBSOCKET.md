# WebSocket API

API WebSocket realtime - streaming giá cổ phiếu, chỉ số thị trường.

**Base URL:** `/api/v1/ws`

**Tag:** `WebSocket`

---

## WebSocket Endpoints

### 1. Price Stream - Streaming giá realtime

```
WebSocket: ws://localhost:8000/api/v1/ws/prices
```

Kết nối WebSocket để nhận dữ liệu giá cổ phiếu realtime.

#### Connection Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbols` | string | null | Danh sách mã cổ phiếu, phân cách bằng dấu phẩy |
| `compress` | boolean | true | Bật nén gzip cho message lớn |

#### Connection Example

```
ws://localhost:8000/api/v1/ws/prices?symbols=VNM,FPT,VCB&compress=true
```

---

### Messages from Server

#### Price Update

```json
{
  "type": "price",
  "data": {
    "event_type": "stock",
    "symbol": "VNM",
    "last_price": 85000,
    "change": 500,
    "change_percent": 0.59,
    "volume": 1250000,
    "value": 106250000000,
    "bid_price_1": 85400,
    "bid_volume_1": 1000,
    "ask_price_1": 85500,
    "ask_volume_1": 800,
    "ceiling": 90000,
    "floor": 80000,
    "ref": 85000,
    "open": 84500,
    "high": 86000,
    "low": 84000,
    "foreign_buy_volume": 50000,
    "foreign_sell_volume": 30000,
    "timestamp": "2024-01-15T14:45:00Z"
  }
}
```

#### Index Update

```json
{
  "type": "index",
  "data": {
    "event_type": "index",
    "index_id": "VNINDEX",
    "current_index": 1256.78,
    "change": 12.34,
    "change_percent": 0.99,
    "total_volume": 450000000,
    "total_value": 12500000000000,
    "advances": 180,
    "declines": 120,
    "no_change": 50,
    "timestamp": "2024-01-15T14:45:00Z"
  }
}
```

#### Cached Prices (on subscribe)

```json
{
  "type": "cached_prices",
  "data": {
    "VNM": {
      "symbol": "VNM",
      "last_price": 85000,
      "change": 500,
      "volume": 1250000
    },
    "FPT": {
      "symbol": "FPT",
      "last_price": 125000,
      "change": 1500,
      "volume": 850000
    }
  },
  "count": 2
}
```

#### Subscribe Response

```json
{
  "type": "subscribed",
  "success": true,
  "subscribed": 3,
  "total": 5,
  "remaining_quota": 995
}
```

#### Unsubscribe Response

```json
{
  "type": "unsubscribed",
  "success": true,
  "unsubscribed": 2,
  "remaining": 3
}
```

#### Pong (heartbeat)

```json
{
  "type": "pong",
  "timestamp": 1705326300.123
}
```

#### Stats

```json
{
  "type": "stats",
  "data": {
    "ip": "192.168.1.100",
    "connected_duration": 3600.5,
    "compression_enabled": true,
    "messages_sent": 15000,
    "bytes_sent": 2500000,
    "subscribed_count": 10,
    "rate_limit_remaining": 25
  }
}
```

#### Error

```json
{
  "type": "error",
  "message": "Rate limit exceeded",
  "valid_actions": ["subscribe", "unsubscribe", "ping", "get_cached", "get_indices", "get_stats"]
}
```

---

### Messages to Server

#### Subscribe to Symbols

```json
{
  "action": "subscribe",
  "symbols": ["ACB", "TCB", "MBB"]
}
```

#### Unsubscribe from Symbols

```json
{
  "action": "unsubscribe",
  "symbols": ["VNM"]
}
```

#### Ping (heartbeat)

```json
{
  "action": "ping"
}
```

#### Get Cached Prices

```json
{
  "action": "get_cached"
}
```

#### Get All Indices

```json
{
  "action": "get_indices"
}
```

#### Get Connection Stats

```json
{
  "action": "get_stats"
}
```

---

## REST Endpoints (Stream Management)

### 2. Get Stream Status

```
GET /api/v1/ws/stream/status
```

Lấy trạng thái kết nối stream và thống kê.

#### Response

```json
{
  "stream": {
    "status": "connected",
    "stats": {
      "is_connected": true,
      "subscribed_symbols": 150,
      "cached_prices": 150,
      "last_message_at": "2024-01-15T14:45:00Z"
    }
  },
  "connections": {
    "total_connections": 25,
    "total_subscriptions": 1500,
    "total_messages_sent": 500000,
    "total_bytes_sent": 125000000,
    "pool_stats": {
      "total_connections": 25,
      "unique_ips": 15,
      "connections_by_ip": {
        "192.168.1.100": 3,
        "192.168.1.101": 2
      }
    }
  },
  "config": {
    "max_symbols_per_client": 1000,
    "batch_size": 100,
    "rate_limit_window": 60,
    "rate_limit_max_requests": 30,
    "compression_threshold": 1024,
    "max_connections_per_ip": 10
  }
}
```

---

### 3. Connect Stream

```
POST /api/v1/ws/stream/connect
```

Kết nối đến nguồn dữ liệu giá.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `market` | string | `HOSE` | Sàn: `HOSE`, `HNX`, `UPCOM` |

#### Response

```json
{
  "status": "connecting",
  "market": "HOSE",
  "stats": {
    "is_connected": false,
    "subscribed_symbols": 0,
    "cached_prices": 0
  }
}
```

---

### 4. Disconnect Stream

```
POST /api/v1/ws/stream/disconnect
```

Ngắt kết nối stream.

#### Response

```json
{
  "status": "disconnected"
}
```

---

### 5. Subscribe Symbols (REST)

```
POST /api/v1/ws/stream/subscribe
```

Subscribe các mã cổ phiếu qua REST API.

#### Request Body

```json
["VNM", "FPT", "VCB", "HPG", "VIC"]
```

#### Response

```json
{
  "subscribed": 5,
  "total_subscribed": 150
}
```

---

### 6. Get Cached Prices (REST)

```
GET /api/v1/ws/stream/prices
```

Lấy giá đã cache từ stream.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbols` | string | null | Danh sách mã (phân cách bằng dấu phẩy), để trống = lấy tất cả |

#### Response

```json
{
  "prices": {
    "VNM": {
      "symbol": "VNM",
      "last_price": 85000,
      "change": 500,
      "change_percent": 0.59,
      "volume": 1250000
    },
    "FPT": {
      "symbol": "FPT",
      "last_price": 125000,
      "change": 1500,
      "change_percent": 1.21,
      "volume": 850000
    }
  },
  "count": 2
}
```

---

## Configuration

| Config | Value | Description |
|--------|-------|-------------|
| `max_symbols_per_client` | 1000 | Số mã tối đa mỗi client được subscribe |
| `batch_size` | 100 | Số mã subscribe mỗi batch |
| `rate_limit_window` | 60s | Cửa sổ rate limit |
| `rate_limit_max_requests` | 30 | Số request tối đa trong cửa sổ |
| `compression_threshold` | 1024 bytes | Ngưỡng nén gzip |
| `max_connections_per_ip` | 10 | Số kết nối tối đa mỗi IP |

---

## Rate Limiting

- **30 requests/minute** cho subscribe/unsubscribe
- Vượt quá sẽ nhận response:

```json
{
  "type": "subscribed",
  "success": false,
  "error": "Rate limit exceeded",
  "retry_after": 60,
  "remaining": 0
}
```

---

## Compression

- Message > 1KB được nén bằng gzip
- Gửi dưới dạng binary WebSocket frame
- Client cần gunzip để decompress:

```javascript
// JavaScript
const decompressed = pako.ungzip(binaryData, { to: 'string' });
const message = JSON.parse(decompressed);
```

```python
# Python
import gzip
decompressed = gzip.decompress(binary_data)
message = json.loads(decompressed)
```

---

## Code Examples

### JavaScript/TypeScript

```typescript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/prices?symbols=VNM,FPT,VCB&compress=true');

ws.onopen = () => {
  console.log('Connected');

  // Subscribe to more symbols
  ws.send(JSON.stringify({
    action: 'subscribe',
    symbols: ['ACB', 'TCB', 'MBB']
  }));
};

ws.onmessage = async (event) => {
  let message;

  // Check if compressed (binary)
  if (event.data instanceof Blob) {
    const buffer = await event.data.arrayBuffer();
    const decompressed = pako.ungzip(new Uint8Array(buffer), { to: 'string' });
    message = JSON.parse(decompressed);
  } else {
    message = JSON.parse(event.data);
  }

  switch (message.type) {
    case 'price':
      console.log(`${message.data.symbol}: ${message.data.last_price}`);
      break;
    case 'index':
      console.log(`${message.data.index_id}: ${message.data.current_index}`);
      break;
    case 'cached_prices':
      console.log(`Received ${message.count} cached prices`);
      break;
    case 'error':
      console.error(message.message);
      break;
  }
};

// Heartbeat
setInterval(() => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ action: 'ping' }));
  }
}, 30000);

// Unsubscribe
ws.send(JSON.stringify({
  action: 'unsubscribe',
  symbols: ['VNM']
}));

// Get stats
ws.send(JSON.stringify({ action: 'get_stats' }));
```

### Python

```python
import asyncio
import gzip
import json
import websockets

async def connect_price_stream():
    uri = "ws://localhost:8000/api/v1/ws/prices?symbols=VNM,FPT,VCB&compress=true"

    async with websockets.connect(uri) as ws:
        # Subscribe to more symbols
        await ws.send(json.dumps({
            "action": "subscribe",
            "symbols": ["ACB", "TCB", "MBB"]
        }))

        async for message in ws:
            # Check if compressed (bytes)
            if isinstance(message, bytes):
                decompressed = gzip.decompress(message)
                data = json.loads(decompressed)
            else:
                data = json.loads(message)

            msg_type = data.get("type")

            if msg_type == "price":
                symbol = data["data"]["symbol"]
                price = data["data"]["last_price"]
                print(f"{symbol}: {price:,}")

            elif msg_type == "index":
                index_id = data["data"]["index_id"]
                value = data["data"]["current_index"]
                print(f"{index_id}: {value:.2f}")

            elif msg_type == "cached_prices":
                print(f"Received {data['count']} cached prices")

            elif msg_type == "error":
                print(f"Error: {data['message']}")

# Run
asyncio.run(connect_price_stream())
```

### cURL (REST endpoints)

```bash
# Get stream status
curl -X GET http://localhost:8000/api/v1/ws/stream/status

# Connect to stream
curl -X POST "http://localhost:8000/api/v1/ws/stream/connect?market=HOSE"

# Subscribe symbols via REST
curl -X POST http://localhost:8000/api/v1/ws/stream/subscribe \
  -H "Content-Type: application/json" \
  -d '["VNM", "FPT", "VCB"]'

# Get cached prices
curl -X GET "http://localhost:8000/api/v1/ws/stream/prices?symbols=VNM,FPT,VCB"

# Get all cached prices
curl -X GET http://localhost:8000/api/v1/ws/stream/prices

# Disconnect stream
curl -X POST http://localhost:8000/api/v1/ws/stream/disconnect
```

---

## Best Practices

1. **Heartbeat**: Gửi ping mỗi 30 giây để giữ kết nối
2. **Reconnection**: Tự động reconnect khi mất kết nối
3. **Batching**: Subscribe theo batch thay vì từng mã
4. **Compression**: Bật compression cho ứng dụng production
5. **Rate Limiting**: Theo dõi `remaining_quota` để tránh bị block
6. **Cleanup**: Unsubscribe khi không cần theo dõi mã nữa

# Quotes API

API lấy dữ liệu giá cổ phiếu - lịch sử giá, giao dịch trong ngày, bảng giá realtime.

**Base URL:** `/api/v1/quotes`

**Tag:** `Quotes`

---

## Endpoints

### 1. Get History - Lấy lịch sử giá OHLCV

```
GET /api/v1/quotes/{symbol}/history
```

Lấy dữ liệu lịch sử giá OHLCV (Open, High, Low, Close, Volume).

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | string | Mã cổ phiếu (VNM, FPT, VCB...) |

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `start` | string | Yes | - | Ngày bắt đầu (YYYY-MM-DD) |
| `end` | string | No | today | Ngày kết thúc (YYYY-MM-DD) |
| `interval` | string | No | `1D` | Khung thời gian: `1m`, `5m`, `15m`, `30m`, `1H`, `1D`, `1W`, `1M` |
| `count_back` | int | No | null | Số nến lấy về (1-5000) |

#### Response

```json
{
  "symbol": "VNM",
  "interval": "1D",
  "data": [
    {
      "time": "2024-12-02T00:00:00",
      "open": 59.13,
      "high": 59.31,
      "low": 58.76,
      "close": 59.04,
      "volume": 1232443
    },
    {
      "time": "2024-12-03T00:00:00",
      "open": 59.13,
      "high": 59.13,
      "low": 58.49,
      "close": 58.49,
      "volume": 2427726
    }
  ]
}
```

**Lưu ý quan trọng:**
- Giá trả về theo đơn vị nghìn VND (ví dụ: 59.04 = 59,040 VND)
- Thời gian theo format ISO 8601

#### Intervals

| Interval | Description |
|----------|-------------|
| `1m` | 1 phút |
| `5m` | 5 phút |
| `15m` | 15 phút |
| `30m` | 30 phút |
| `1H` | 1 giờ |
| `1D` | 1 ngày |
| `1W` | 1 tuần |
| `1M` | 1 tháng |

---

### 2. Get Intraday - Lấy giao dịch trong ngày

```
GET /api/v1/quotes/{symbol}/intraday
```

Lấy danh sách giao dịch khớp lệnh trong ngày (intraday trades).

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | string | Mã cổ phiếu |

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page_size` | int | 100 | Số giao dịch trả về (1-5000) |
| `last_time` | string | null | Lấy giao dịch sau thời điểm này |

#### Response

```json
{
  "symbol": "VNM",
  "data": [
    {
      "time": "2025-12-26T14:29:51+07:00",
      "price": 61.7,
      "volume": 400,
      "side": null
    },
    {
      "time": "2025-12-26T14:29:59+07:00",
      "price": 61.7,
      "volume": 100,
      "side": null
    },
    {
      "time": "2025-12-26T14:45:00+07:00",
      "price": 61.5,
      "volume": 185700,
      "side": null
    }
  ],
  "count": 3
}
```

| Field | Type | Description |
|-------|------|-------------|
| `time` | string | Thời gian khớp lệnh (ISO 8601 với timezone) |
| `price` | number | Giá khớp (đơn vị nghìn VND) |
| `volume` | number | Khối lượng khớp |
| `side` | string/null | Chiều giao dịch (null nếu không xác định) |

---

### 3. Get Price Board - Bảng giá realtime

```
POST /api/v1/quotes/price-board
```

Lấy bảng giá realtime cho nhiều mã cổ phiếu.

#### Request Body

```json
{
  "symbols": ["VNM", "FPT", "VCB", "HPG"]
}
```

#### Response

```json
{
  "data": [
    {
      "symbol": "VNM",
      "exchange": "HSX",
      "organ_name": "Công ty Cổ phần Sữa Việt Nam",
      "price": null,
      "change": null,
      "change_percent": null,
      "volume": null,
      "value": null,
      "ref_price": null,
      "ceiling": null,
      "floor": null,
      "open": 61600.0,
      "high": null,
      "low": null,
      "bid_1_price": 61500.0,
      "bid_1_volume": 49800,
      "bid_2_price": 61400.0,
      "bid_2_volume": 43000,
      "bid_3_price": 61300.0,
      "bid_3_volume": 65400,
      "ask_1_price": 61700.0,
      "ask_1_volume": 20000,
      "ask_2_price": 61800.0,
      "ask_2_volume": 9500,
      "ask_3_price": 61900.0,
      "ask_3_volume": 1800,
      "foreign_buy_volume": 333720,
      "foreign_sell_volume": 486480
    }
  ],
  "count": 1
}
```

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Mã cổ phiếu |
| `exchange` | string | Sàn giao dịch (HSX, HNX, UPCOM) |
| `organ_name` | string | Tên công ty |
| `price` | number/null | Giá hiện tại (VND) |
| `change` | number/null | Thay đổi giá |
| `change_percent` | number/null | % thay đổi |
| `volume` | number/null | Khối lượng giao dịch |
| `value` | number/null | Giá trị giao dịch |
| `ref_price` | number/null | Giá tham chiếu |
| `ceiling` | number/null | Giá trần |
| `floor` | number/null | Giá sàn |
| `open` | number | Giá mở cửa |
| `high` | number/null | Giá cao nhất |
| `low` | number/null | Giá thấp nhất |
| `bid_1_price` | number | Giá mua tốt nhất |
| `bid_1_volume` | number | KL mua tại giá bid_1 |
| `bid_2_price` | number | Giá mua thứ 2 |
| `bid_2_volume` | number | KL mua tại giá bid_2 |
| `bid_3_price` | number | Giá mua thứ 3 |
| `bid_3_volume` | number | KL mua tại giá bid_3 |
| `ask_1_price` | number | Giá bán tốt nhất |
| `ask_1_volume` | number | KL bán tại giá ask_1 |
| `ask_2_price` | number | Giá bán thứ 2 |
| `ask_2_volume` | number | KL bán tại giá ask_2 |
| `ask_3_price` | number | Giá bán thứ 3 |
| `ask_3_volume` | number | KL bán tại giá ask_3 |
| `foreign_buy_volume` | number | KL mua khối ngoại |
| `foreign_sell_volume` | number | KL bán khối ngoại |

**Lưu ý:** Giá trong Price Board trả về theo VND thực (không chia 1000)

---

### 4. Get Price Depth - Độ sâu giá

```
GET /api/v1/quotes/{symbol}/depth
```

Lấy thông tin độ sâu giá (order book) - phân bổ khối lượng theo từng mức giá.

#### Response

```json
{
  "symbol": "VNM",
  "data": [
    {
      "price": 62300.0,
      "volume": 8100,
      "buy_volume": 8100,
      "sell_volume": 0
    },
    {
      "price": 62200.0,
      "volume": 87800,
      "buy_volume": 58700,
      "sell_volume": 29100
    },
    {
      "price": 62100.0,
      "volume": 189900,
      "buy_volume": 102300,
      "sell_volume": 87600
    },
    {
      "price": 62000.0,
      "volume": 316900,
      "buy_volume": 208000,
      "sell_volume": 108900
    },
    {
      "price": 61900.0,
      "volume": 196200,
      "buy_volume": 148400,
      "sell_volume": 47800
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `price` | number | Mức giá (VND) |
| `volume` | number | Tổng khối lượng tại mức giá |
| `buy_volume` | number | Khối lượng mua tại mức giá |
| `sell_volume` | number | Khối lượng bán tại mức giá |

---

### 5. Get Trading Stats - Thống kê giao dịch

```
GET /api/v1/quotes/{symbol}/trading-stats
```

Lấy thống kê giao dịch theo thời gian.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `resolution` | string | `1D` | Độ phân giải: `1D`, `1W`, `1M` |
| `start` | string | null | Ngày bắt đầu (YYYY-MM-DD) |
| `end` | string | null | Ngày kết thúc (YYYY-MM-DD) |
| `limit` | int | 100 | Số kết quả (1-1000) |

#### Response

```json
{
  "symbol": "VNM",
  "data": [
    {
      "trading_date": "2025-12-25T00:00:00",
      "open": 61600.0,
      "high": 62300.0,
      "low": 61300.0,
      "close": 61300.0,
      "matched_volume": 2065300,
      "matched_value": 127355579000.0,
      "deal_volume": 310200,
      "deal_value": 19663800000.0
    },
    {
      "trading_date": "2025-12-24T00:00:00",
      "open": 62800.0,
      "high": 62900.0,
      "low": 61500.0,
      "close": 61500.0,
      "matched_volume": 4879706,
      "matched_value": 301730454000.0,
      "deal_volume": 90000,
      "deal_value": 6007500000.0
    }
  ],
  "count": 2
}
```

| Field | Type | Description |
|-------|------|-------------|
| `trading_date` | string | Ngày giao dịch (ISO 8601) |
| `open` | number | Giá mở cửa (VND) |
| `high` | number | Giá cao nhất (VND) |
| `low` | number | Giá thấp nhất (VND) |
| `close` | number | Giá đóng cửa (VND) |
| `matched_volume` | number | Khối lượng khớp lệnh |
| `matched_value` | number | Giá trị khớp lệnh (VND) |
| `deal_volume` | number | Khối lượng thỏa thuận |
| `deal_value` | number | Giá trị thỏa thuận (VND) |

---

## Caching

Dữ liệu được cache để tối ưu performance:

| Data Type | Cache TTL |
|-----------|-----------|
| Price Board | 5 giây |
| Intraday | 10 giây |
| History (recent) | 5 phút |
| History (old) | 1 giờ |

---

## Code Examples

### cURL

```bash
# Get history
curl -X GET "http://localhost:8000/api/v1/quotes/VNM/history?start=2024-01-01&end=2024-01-15&interval=1D"

# Get intraday
curl -X GET "http://localhost:8000/api/v1/quotes/VNM/intraday?page_size=100"

# Get price board
curl -X POST http://localhost:8000/api/v1/quotes/price-board \
  -H "Content-Type: application/json" \
  -d '{"symbols":["VNM","FPT","VCB"]}'

# Get price depth
curl -X GET http://localhost:8000/api/v1/quotes/VNM/depth

# Get trading stats
curl -X GET "http://localhost:8000/api/v1/quotes/VNM/trading-stats?resolution=1D&limit=30"
```

### JavaScript/TypeScript

```typescript
// Get history
const history = await fetch(
  '/api/v1/quotes/VNM/history?start=2024-01-01&interval=1D'
).then(r => r.json());

// Get price board
const priceBoard = await fetch('/api/v1/quotes/price-board', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ symbols: ['VNM', 'FPT', 'VCB'] })
}).then(r => r.json());

// Get intraday trades
const intraday = await fetch('/api/v1/quotes/VNM/intraday').then(r => r.json());

// Get depth
const depth = await fetch('/api/v1/quotes/VNM/depth').then(r => r.json());

// Get trading stats
const stats = await fetch('/api/v1/quotes/VNM/trading-stats?limit=30').then(r => r.json());
```

### Python

```python
import httpx

# Get history
history = httpx.get(
    "http://localhost:8000/api/v1/quotes/VNM/history",
    params={"start": "2024-01-01", "end": "2024-01-15", "interval": "1D"}
).json()

# Get price board
price_board = httpx.post(
    "http://localhost:8000/api/v1/quotes/price-board",
    json={"symbols": ["VNM", "FPT", "VCB"]}
).json()

# Get intraday
intraday = httpx.get(
    "http://localhost:8000/api/v1/quotes/VNM/intraday",
    params={"page_size": 100}
).json()

# Get depth
depth = httpx.get("http://localhost:8000/api/v1/quotes/VNM/depth").json()

# Get trading stats
stats = httpx.get(
    "http://localhost:8000/api/v1/quotes/VNM/trading-stats",
    params={"resolution": "1D", "limit": 30}
).json()
```

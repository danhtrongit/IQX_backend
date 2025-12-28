# Insight API

API phân tích thị trường - top foreign, top gainer/loser, giao dịch tự doanh/khối ngoại.

**Base URL:** `/api/v1/insight`

**Tag:** `Insight`

---

## Endpoints

### 1. Top Foreign Buy - Top mua ròng khối ngoại

```
GET /api/v1/insight/top/foreign-buy
```

Lấy danh sách cổ phiếu được khối ngoại mua ròng nhiều nhất.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `date` | string | today | Ngày (YYYY-MM-DD) |
| `limit` | int | 10 | Số kết quả (1-50) |

#### Response

```json
{
  "type": "buy",
  "date": "2025-12-26",
  "data": [
    {
      "symbol": "VJC",
      "date": "2025-12-26",
      "net_value": 67253426800.0
    },
    {
      "symbol": "VCB",
      "date": "2025-12-26",
      "net_value": 52000000000.0
    }
  ],
  "count": 2
}
```

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Mã cổ phiếu |
| `date` | string | Ngày giao dịch (YYYY-MM-DD) |
| `net_value` | number | Giá trị mua ròng (VND) |

---

### 2. Top Foreign Sell - Top bán ròng khối ngoại

```
GET /api/v1/insight/top/foreign-sell
```

Lấy danh sách cổ phiếu bị khối ngoại bán ròng nhiều nhất.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `date` | string | today | Ngày (YYYY-MM-DD) |
| `limit` | int | 10 | Số kết quả (1-50) |

#### Response

```json
{
  "type": "sell",
  "date": "2025-12-26",
  "data": [
    {
      "symbol": "HPG",
      "date": "2025-12-26",
      "net_value": -65000000000.0
    },
    {
      "symbol": "SSI",
      "date": "2025-12-26",
      "net_value": -42000000000.0
    }
  ],
  "count": 2
}
```

**Lưu ý:** `net_value` là số âm cho bán ròng

---

### 3. Top Gainer - Cổ phiếu tăng giá mạnh nhất

```
GET /api/v1/insight/top/gainer
```

Lấy danh sách cổ phiếu tăng giá mạnh nhất.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `index` | string | `VNINDEX` | Chỉ số: `VNINDEX`, `HNXINDEX`, `UPCOMINDEX` |
| `limit` | int | 10 | Số kết quả (1-50) |

#### Response

```json
{
  "type": "gainer",
  "index": "VNINDEX",
  "data": [
    {
      "symbol": "C47",
      "last_price": 9.63,
      "price_change_1d": 0.63,
      "price_change_pct_1d": 7.0,
      "accumulated_value": 268973000.0,
      "avg_volume_20d": 22418.9,
      "volume_spike_20d_pct": 88.76
    },
    {
      "symbol": "STB",
      "last_price": 42.65,
      "price_change_1d": 2.75,
      "price_change_pct_1d": 6.89,
      "accumulated_value": 1248000000000.0,
      "avg_volume_20d": 15000000.0,
      "volume_spike_20d_pct": 125.5
    }
  ],
  "count": 2
}
```

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Mã cổ phiếu |
| `last_price` | number | Giá hiện tại (đơn vị nghìn VND) |
| `price_change_1d` | number | Thay đổi giá trong ngày |
| `price_change_pct_1d` | number | % thay đổi giá |
| `accumulated_value` | number | Giá trị giao dịch (VND) |
| `avg_volume_20d` | number | Khối lượng trung bình 20 phiên |
| `volume_spike_20d_pct` | number | % đột biến so với TB 20 phiên |

---

### 4. Top Loser - Cổ phiếu giảm giá mạnh nhất

```
GET /api/v1/insight/top/loser
```

Lấy danh sách cổ phiếu giảm giá mạnh nhất.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `index` | string | `VNINDEX` | Chỉ số: `VNINDEX`, `HNXINDEX`, `UPCOMINDEX` |
| `limit` | int | 10 | Số kết quả (1-50) |

#### Response

```json
{
  "type": "loser",
  "index": "VNINDEX",
  "data": [
    {
      "symbol": "XYZ",
      "last_price": 18.0,
      "price_change_1d": -1.26,
      "price_change_pct_1d": -7.0,
      "accumulated_value": 8000000000.0,
      "avg_volume_20d": 50000.0,
      "volume_spike_20d_pct": 120.5
    }
  ],
  "count": 1
}
```

---

### 5. Top Value - Cổ phiếu có giá trị giao dịch cao nhất

```
GET /api/v1/insight/top/value
```

Lấy danh sách cổ phiếu có giá trị giao dịch cao nhất.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `index` | string | `VNINDEX` | Chỉ số: `VNINDEX`, `HNXINDEX`, `UPCOMINDEX` |
| `limit` | int | 10 | Số kết quả (1-50) |

#### Response

```json
{
  "type": "value",
  "index": "VNINDEX",
  "data": [
    {
      "symbol": "VNM",
      "last_price": 61.5,
      "price_change_1d": 0.5,
      "price_change_pct_1d": 0.82,
      "accumulated_value": 250000000000.0,
      "avg_volume_20d": 1050000.0,
      "volume_spike_20d_pct": 150.0
    }
  ],
  "count": 1
}
```

---

### 6. Top Volume - Cổ phiếu có khối lượng giao dịch bất thường

```
GET /api/v1/insight/top/volume
```

Lấy danh sách cổ phiếu có khối lượng giao dịch đột biến so với trung bình 20 phiên.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `index` | string | `VNINDEX` | Chỉ số: `VNINDEX`, `HNXINDEX`, `UPCOMINDEX` |
| `limit` | int | 10 | Số kết quả (1-50) |

#### Response

```json
{
  "type": "volume",
  "index": "VNINDEX",
  "data": [
    {
      "symbol": "FPT",
      "last_price": 125.0,
      "price_change_1d": 2.5,
      "price_change_pct_1d": 2.04,
      "accumulated_value": 500000000000.0,
      "avg_volume_20d": 500000.0,
      "volume_spike_20d_pct": 350.5
    }
  ],
  "count": 1
}
```

---

### 7. Top Deal - Cổ phiếu có giao dịch thỏa thuận lớn

```
GET /api/v1/insight/top/deal
```

Lấy danh sách cổ phiếu có khối lượng giao dịch thỏa thuận lớn nhất.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `index` | string | `VNINDEX` | Chỉ số: `VNINDEX`, `HNXINDEX`, `UPCOMINDEX` |
| `limit` | int | 10 | Số kết quả (1-50) |

#### Response

```json
{
  "type": "deal",
  "index": "VNINDEX",
  "data": [
    {
      "symbol": "VCB",
      "last_price": 95.0,
      "price_change_1d": 1.5,
      "price_change_pct_1d": 1.6,
      "accumulated_value": 180000000000.0,
      "avg_volume_20d": 2000000.0,
      "volume_spike_20d_pct": 80.0
    }
  ],
  "count": 1
}
```

---

### 8. Proprietary Trading - Giao dịch tự doanh

```
GET /api/v1/insight/{symbol}/proprietary
```

Lấy lịch sử giao dịch tự doanh (CTCK) của một mã cổ phiếu.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | string | Mã cổ phiếu |

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start` | string | null | Ngày bắt đầu (YYYY-MM-DD) |
| `end` | string | null | Ngày kết thúc (YYYY-MM-DD) |
| `limit` | int | 30 | Số kết quả (1-100) |

#### Response

```json
{
  "symbol": "VNM",
  "data": [
    {
      "trading_date": "2025-12-25T00:00:00",
      "buy_volume": 150000,
      "buy_value": 12750000000.0,
      "sell_volume": 80000,
      "sell_value": 6800000000.0,
      "net_volume": 70000,
      "net_value": 5950000000.0
    },
    {
      "trading_date": "2025-12-24T00:00:00",
      "buy_volume": 100000,
      "buy_value": 8500000000.0,
      "sell_volume": 120000,
      "sell_value": 10200000000.0,
      "net_volume": -20000,
      "net_value": -1700000000.0
    }
  ],
  "count": 2
}
```

| Field | Type | Description |
|-------|------|-------------|
| `trading_date` | string | Ngày giao dịch (ISO 8601) |
| `buy_volume` | number | Khối lượng mua |
| `buy_value` | number | Giá trị mua (VND) |
| `sell_volume` | number | Khối lượng bán |
| `sell_value` | number | Giá trị bán (VND) |
| `net_volume` | number | Khối lượng ròng |
| `net_value` | number | Giá trị ròng (VND) |

---

### 9. Foreign Trading - Giao dịch khối ngoại theo mã

```
GET /api/v1/insight/{symbol}/foreign
```

Lấy lịch sử giao dịch khối ngoại của một mã cổ phiếu.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | string | Mã cổ phiếu |

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start` | string | null | Ngày bắt đầu (YYYY-MM-DD) |
| `end` | string | null | Ngày kết thúc (YYYY-MM-DD) |
| `limit` | int | 30 | Số kết quả (1-100) |

#### Response

```json
{
  "symbol": "VNM",
  "data": [
    {
      "trading_date": "2024-01-15",
      "buy_volume": 500000,
      "buy_value": 42500000000,
      "sell_volume": 350000,
      "sell_value": 29750000000,
      "net_volume": 150000,
      "net_value": 12750000000,
      "total_room": 1045000000,
      "current_room": 520000000,
      "owned_percent": 49.00
    }
  ],
  "count": 30
}
```

| Field | Type | Description |
|-------|------|-------------|
| `total_room` | number | Tổng room khối ngoại |
| `current_room` | number | Room còn lại |
| `owned_percent` | number | Tỷ lệ sở hữu nước ngoài (%) |

---

### 10. Order Stats - Thống kê lệnh

```
GET /api/v1/insight/{symbol}/orders
```

Lấy thống kê lệnh theo loại (ATO, ATC, LO, MP).

#### Response

```json
{
  "symbol": "VNM",
  "data": [
    {
      "order_type": "LO",
      "count": 5420,
      "volume": 2500000
    },
    {
      "order_type": "ATO",
      "count": 120,
      "volume": 450000
    },
    {
      "order_type": "ATC",
      "count": 85,
      "volume": 380000
    }
  ],
  "count": 3
}
```

---

### 11. Side Stats - Thống kê theo chiều mua/bán

```
GET /api/v1/insight/{symbol}/sides
```

Lấy thống kê khối lượng mua/bán.

#### Response

```json
{
  "symbol": "VNM",
  "data": [
    {
      "side": "BUY",
      "volume": 1800000,
      "value": 153000000000
    },
    {
      "side": "SELL",
      "volume": 1650000,
      "value": 140250000000
    }
  ],
  "count": 2
}
```

---

## Caching

| Data Type | Cache TTL |
|-----------|-----------|
| Top Stocks (gainer, loser, value, volume) | 5 phút |
| Foreign/Proprietary Trading | 5 phút |
| Order/Side Stats | 10 giây |

---

## Code Examples

### cURL

```bash
# Get top foreign buy
curl -X GET "http://localhost:8000/api/v1/insight/top/foreign-buy?limit=10"

# Get top gainers on VNINDEX
curl -X GET "http://localhost:8000/api/v1/insight/top/gainer?index=VNINDEX&limit=10"

# Get top losers on HNX
curl -X GET "http://localhost:8000/api/v1/insight/top/loser?index=HNXINDEX&limit=5"

# Get top volume
curl -X GET "http://localhost:8000/api/v1/insight/top/volume?index=VNINDEX&limit=10"

# Get proprietary trading for VNM
curl -X GET "http://localhost:8000/api/v1/insight/VNM/proprietary?limit=30"

# Get foreign trading for FPT
curl -X GET "http://localhost:8000/api/v1/insight/FPT/foreign?start=2024-01-01&limit=20"

# Get order stats
curl -X GET http://localhost:8000/api/v1/insight/VNM/orders

# Get side stats
curl -X GET http://localhost:8000/api/v1/insight/VNM/sides
```

### JavaScript/TypeScript

```typescript
// Get top foreign buy
const topForeignBuy = await fetch(
  '/api/v1/insight/top/foreign-buy?limit=10'
).then(r => r.json());

// Get top gainers
const topGainers = await fetch(
  '/api/v1/insight/top/gainer?index=VNINDEX&limit=10'
).then(r => r.json());

// Get top volume spikes
const topVolume = await fetch(
  '/api/v1/insight/top/volume?index=VNINDEX&limit=10'
).then(r => r.json());

// Get proprietary trading
const proprietary = await fetch(
  '/api/v1/insight/VNM/proprietary?limit=30'
).then(r => r.json());

// Get foreign trading
const foreign = await fetch(
  '/api/v1/insight/FPT/foreign?start=2024-01-01'
).then(r => r.json());
```

### Python

```python
import httpx

# Get top foreign buy
top_buy = httpx.get(
    "http://localhost:8000/api/v1/insight/top/foreign-buy",
    params={"limit": 10}
).json()

# Get top gainers
gainers = httpx.get(
    "http://localhost:8000/api/v1/insight/top/gainer",
    params={"index": "VNINDEX", "limit": 10}
).json()

# Get proprietary trading
proprietary = httpx.get(
    "http://localhost:8000/api/v1/insight/VNM/proprietary",
    params={"limit": 30}
).json()

# Get foreign trading
foreign = httpx.get(
    "http://localhost:8000/api/v1/insight/FPT/foreign",
    params={"start": "2024-01-01", "limit": 20}
).json()

# Get order stats
orders = httpx.get("http://localhost:8000/api/v1/insight/VNM/orders").json()
```

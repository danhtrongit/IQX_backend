# Market API

API thông tin thị trường - chỉ số, tổng quan thị trường, định giá.

**Base URL:** `/api/v1/market`

**Tag:** `Market`

---

## Endpoints

### 1. Get Market Overview - Tổng quan thị trường

```
GET /api/v1/market/overview
```

Lấy tổng quan thị trường với tất cả chỉ số chính.

#### Response

```json
{
  "indices": [
    {
      "index_code": "VNINDEX",
      "index_value": 1729.8,
      "change": -13.05,
      "change_percent": -0.75,
      "ref_value": 1742.85,
      "open_value": 1706.39,
      "high_value": 1730.99,
      "low_value": 1687.14,
      "total_volume": 1081379964,
      "total_value": null,
      "advances": null,
      "declines": null,
      "unchanged": null,
      "foreign_buy_volume": null,
      "foreign_sell_volume": null,
      "foreign_net_volume": null,
      "timestamp": "2025-12-26T14:36:07.131362"
    },
    {
      "index_code": "HNXINDEX",
      "index_value": 250.53,
      "change": -0.45,
      "change_percent": -0.18,
      "ref_value": 250.98,
      "open_value": 250.36,
      "high_value": 251.91,
      "low_value": 246.43,
      "total_volume": 101294699,
      "total_value": null,
      "advances": null,
      "declines": null,
      "unchanged": null,
      "foreign_buy_volume": null,
      "foreign_sell_volume": null,
      "foreign_net_volume": null,
      "timestamp": "2025-12-26T14:36:07.268902"
    },
    {
      "index_code": "UPCOMINDEX",
      "index_value": 119.74,
      "change": 0.03,
      "change_percent": 0.03,
      "ref_value": 119.71,
      "open_value": 119.98,
      "high_value": 120.14,
      "low_value": 118.88,
      "total_volume": 81579474,
      "total_value": null,
      "advances": null,
      "declines": null,
      "unchanged": null,
      "foreign_buy_volume": null,
      "foreign_sell_volume": null,
      "foreign_net_volume": null,
      "timestamp": "2025-12-26T14:36:07.140084"
    },
    {
      "index_code": "VN30",
      "index_value": 1965.97,
      "change": -10.24,
      "change_percent": -0.52,
      "ref_value": 1976.21,
      "open_value": 1941.78,
      "high_value": 1969.07,
      "low_value": 1914.65,
      "total_volume": 544044122,
      "total_value": null,
      "advances": null,
      "declines": null,
      "unchanged": null,
      "foreign_buy_volume": null,
      "foreign_sell_volume": null,
      "foreign_net_volume": null,
      "timestamp": "2025-12-26T14:36:07.145793"
    }
  ],
  "timestamp": "2025-12-26T14:36:07.269062"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `index_code` | string | Mã chỉ số |
| `index_value` | number | Giá trị hiện tại |
| `change` | number | Thay đổi so với phiên trước |
| `change_percent` | number | % thay đổi |
| `ref_value` | number | Giá trị tham chiếu |
| `open_value` | number | Giá mở cửa |
| `high_value` | number | Giá cao nhất |
| `low_value` | number | Giá thấp nhất |
| `total_volume` | number | Tổng khối lượng giao dịch |
| `total_value` | number/null | Tổng giá trị giao dịch |
| `advances` | number/null | Số mã tăng giá |
| `declines` | number/null | Số mã giảm giá |
| `unchanged` | number/null | Số mã đứng giá |
| `foreign_buy_volume` | number/null | KL mua khối ngoại |
| `foreign_sell_volume` | number/null | KL bán khối ngoại |
| `foreign_net_volume` | number/null | KL mua ròng khối ngoại |
| `timestamp` | string | Thời gian cập nhật |

---

### 2. Get Index - Lấy thông tin một chỉ số

```
GET /api/v1/market/indices/{index_code}
```

Lấy thông tin chi tiết một chỉ số.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `index_code` | string | Mã chỉ số: `VNINDEX`, `HNXINDEX`, `UPCOMINDEX`, `VN30` |

#### Response

```json
{
  "index_code": "VNINDEX",
  "index_value": 1729.8,
  "change": 13.05,
  "change_percent": 0.75,
  "ref_value": null,
  "open_value": 1742.85,
  "high_value": null,
  "low_value": null,
  "total_volume": 1081379964,
  "total_value": 32679593.51,
  "advances": 100,
  "declines": 218,
  "unchanged": 54,
  "foreign_buy_volume": null,
  "foreign_sell_volume": null,
  "foreign_net_volume": null,
  "timestamp": "2025-12-26T21:35:35.070880"
}
```

---

### 3. Get Index History - Lịch sử chỉ số

```
GET /api/v1/market/indices/{index_code}/history
```

Lấy dữ liệu lịch sử của chỉ số.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `index_code` | string | Mã chỉ số |

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `start` | string | Yes | - | Ngày bắt đầu (YYYY-MM-DD) |
| `end` | string | No | today | Ngày kết thúc (YYYY-MM-DD) |
| `interval` | string | No | `1D` | Khung thời gian: `1D`, `1W`, `1M` |

#### Response

```json
{
  "index_code": "VNINDEX",
  "data": [
    {
      "time": "2025-12-01T00:00:00",
      "open": 1698.98,
      "high": 1713.77,
      "low": 1697.38,
      "close": 1701.67,
      "volume": 633506422
    },
    {
      "time": "2025-12-02T00:00:00",
      "open": 1704.84,
      "high": 1719.03,
      "low": 1690.36,
      "close": 1717.06,
      "volume": 693931904
    },
    {
      "time": "2025-12-03T00:00:00",
      "open": 1725.9,
      "high": 1741.65,
      "low": 1714.9,
      "close": 1731.77,
      "volume": 822614056
    }
  ],
  "count": 20
}
```

| Field | Type | Description |
|-------|------|-------------|
| `time` | string | Thời gian (ISO 8601) |
| `open` | number | Giá mở cửa |
| `high` | number | Giá cao nhất |
| `low` | number | Giá thấp nhất |
| `close` | number | Giá đóng cửa |
| `volume` | number | Khối lượng giao dịch |

---

### 4. Get Market Evaluation - Định giá thị trường

```
GET /api/v1/market/evaluation
```

Lấy chỉ số định giá thị trường (PE, PB) theo thời gian.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `period` | string | `day` | Chu kỳ: `day`, `week`, `month` |
| `time_window` | string | `1D` | Khung thời gian |

#### Response

```json
{
  "data": [
    {
      "date": null,
      "pe": 17.96576872800023,
      "pb": 2.3890210797601306,
      "ps": null,
      "dy": null,
      "vn_type": null
    },
    {
      "date": null,
      "pe": 18.050562948134576,
      "pb": 2.4067386126033803,
      "ps": null,
      "dy": null,
      "vn_type": null
    },
    {
      "date": null,
      "pe": 18.018503001218654,
      "pb": 2.4029664199948826,
      "ps": null,
      "dy": null,
      "vn_type": null
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `date` | string/null | Ngày |
| `pe` | number | Chỉ số P/E (Price to Earnings) |
| `pb` | number | Chỉ số P/B (Price to Book) |
| `ps` | number/null | Chỉ số P/S (Price to Sales) |
| `dy` | number/null | Tỷ suất cổ tức (Dividend Yield) |
| `vn_type` | string/null | Loại thị trường VN |

---

## Index Codes

| Code | Name | Exchange |
|------|------|----------|
| `VNINDEX` | VN-Index | HOSE |
| `VN30` | VN30-Index | HOSE |
| `HNXINDEX` | HNX-Index | HNX |
| `UPCOMINDEX` | UPCOM-Index | UPCOM |

---

## Caching

| Data Type | Cache TTL |
|-----------|-----------|
| Market Overview | 10 giây |
| Index | 10 giây |
| Index History | 5 phút |
| Market Evaluation | 30 phút |

---

## Code Examples

### cURL

```bash
# Get market overview
curl -X GET http://localhost:8000/api/v1/market/overview

# Get VNINDEX
curl -X GET http://localhost:8000/api/v1/market/indices/VNINDEX

# Get VNINDEX history
curl -X GET "http://localhost:8000/api/v1/market/indices/VNINDEX/history?start=2024-01-01&interval=1D"

# Get market evaluation
curl -X GET "http://localhost:8000/api/v1/market/evaluation?period=day"
```

### JavaScript/TypeScript

```typescript
// Get market overview
const overview = await fetch('/api/v1/market/overview').then(r => r.json());

// Get specific index
const vnindex = await fetch('/api/v1/market/indices/VNINDEX').then(r => r.json());

// Get index history
const history = await fetch(
  '/api/v1/market/indices/VNINDEX/history?start=2024-01-01'
).then(r => r.json());

// Get market evaluation
const evaluation = await fetch('/api/v1/market/evaluation').then(r => r.json());
```

### Python

```python
import httpx

# Get market overview
overview = httpx.get("http://localhost:8000/api/v1/market/overview").json()

# Get VNINDEX
vnindex = httpx.get("http://localhost:8000/api/v1/market/indices/VNINDEX").json()

# Get index history
history = httpx.get(
    "http://localhost:8000/api/v1/market/indices/VNINDEX/history",
    params={"start": "2024-01-01", "interval": "1D"}
).json()

# Get market evaluation
evaluation = httpx.get(
    "http://localhost:8000/api/v1/market/evaluation",
    params={"period": "day"}
).json()
```

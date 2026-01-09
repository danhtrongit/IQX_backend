# Score API Documentation

## Overview

Score API cung cấp 2 endpoints để phân tích và xếp hạng cổ phiếu dựa trên công thức kết hợp giá và khối lượng.

## Công thức Score

```
SCORE = P × √V
```

Trong đó:
- **P** = ((Close - MA) / MA) × 100 — Độ lệch giá so với MA (%)
- **V** = Volume / Vol_Avg — Tỷ lệ khối lượng so với trung bình

**Ví dụ:**
- Close = 75,000 | MA20 = 69,300 → P = 8.23%
- Volume = 5,200,000 | Vol_MA20 = 2,260,000 → V = 2.3
- SCORE = 8.23 × √2.3 = **12.5**

**Ý nghĩa:**
- Score > 0: Giá đang trên MA, có thể đang uptrend
- Score < 0: Giá đang dưới MA, có thể đang downtrend
- Score cao + V cao: Breakout với volume mạnh

---

## API Endpoints

### 1. Score Ranking

Xếp hạng tất cả cổ phiếu theo score.

```
GET /api/v1/score/ranking
```

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| ma_period | int | Yes | - | MA period: 5, 10, 20, 30, 50, 100, 200 |
| exchange | string | No | ALL | Sàn: HOSE, HNX, UPCOM (comma-separated) |
| limit | int | No | 50 | Số lượng kết quả (1-500) |
| offset | int | No | 0 | Offset cho pagination |
| sort | string | No | desc | Sắp xếp: desc (cao→thấp), asc (thấp→cao) |

**Lưu ý:**
- Chỉ trả về cổ phiếu có volume >= 500,000
- `exchange=HOSE` tự động map sang HSX trong database

**Request Example:**
```
GET /api/v1/score/ranking?ma_period=20&exchange=HOSE&limit=10&sort=desc
```

**Response:**
```json
{
  "items": [
    {
      "rank": 1,
      "symbol": "VCB",
      "exchange": "HSX",
      "score": 12.5,
      "p": 8.23,
      "v": 2.3,
      "close": "75000.00",
      "ma": "69300.00",
      "volume": 5200000,
      "vol_avg": 2260000
    }
  ],
  "total": 108,
  "ma_period": 20,
  "trade_date": "2026-01-09"
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| rank | Thứ hạng theo score |
| symbol | Mã cổ phiếu |
| exchange | Sàn giao dịch (HSX, HNX, UPCOM) |
| score | Điểm score = P × √V |
| p | Độ lệch giá so với MA (%) |
| v | Tỷ lệ volume so với trung bình |
| close | Giá đóng cửa |
| ma | Giá trị MA |
| volume | Khối lượng giao dịch |
| vol_avg | Khối lượng trung bình |
| total | Tổng số cổ phiếu thỏa điều kiện |
| trade_date | Ngày giao dịch của dữ liệu |

---

### 2. Score History

Lịch sử score của một cổ phiếu theo thời gian.

```
GET /api/v1/score/history/{symbol}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| symbol | string | Mã cổ phiếu (VD: VNM, VCB) |

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| ma_period | int | Yes | - | MA period: 5, 10, 20, 30, 50, 100 (không có 200) |
| range | string | Yes | - | Khoảng thời gian: week, month, year |

**Request Example:**
```
GET /api/v1/score/history/VNM?ma_period=20&range=month
```

**Response:**
```json
{
  "symbol": "VNM",
  "ma_period": 20,
  "data": [
    {
      "date": "2026-01-05",
      "score": -2.96,
      "p": -3.26,
      "v": 0.82,
      "close": "60300.00",
      "ma": "62335.00",
      "volume": 2814700,
      "vol_avg": 3428450
    },
    {
      "date": "2026-01-06",
      "score": -2.11,
      "p": -2.26,
      "v": 0.87,
      "close": "60800.00",
      "ma": "62205.00",
      "volume": 2963300,
      "vol_avg": 3396670
    }
  ]
}
```

---

## OHLC Sync Service

### Scheduler

Tự động chạy lúc **16:00** hàng ngày (sau khi thị trường đóng cửa):
- Sync dữ liệu OHLC mới nhất
- Tự động fill gaps nếu bỏ lỡ ngày nào
- Tính MA cho tất cả các ngày mới

### CLI Commands

```bash
# Full sync (200 ngày, tất cả mã)
python -m scripts.ohlc_sync full

# Daily sync (chỉ hôm nay + fill gaps)
python -m scripts.ohlc_sync daily

# Kiểm tra status
python -m scripts.ohlc_sync status

# Tính MA thủ công
python -m scripts.ohlc_sync calculate-ma

# Tính MA cho ngày cụ thể
python -m scripts.ohlc_sync calculate-ma --date 2026-01-09

# Kiểm tra gaps
python -m scripts.ohlc_sync gaps

# Fill gaps
python -m scripts.ohlc_sync fill-gaps
```

### Database Schema

**Table: stock_ohlc_daily**

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT | Primary key |
| symbol | VARCHAR(20) | Mã cổ phiếu |
| trade_date | DATE | Ngày giao dịch |
| open | DECIMAL(12,2) | Giá mở cửa |
| high | DECIMAL(12,2) | Giá cao nhất |
| low | DECIMAL(12,2) | Giá thấp nhất |
| close | DECIMAL(12,2) | Giá đóng cửa |
| volume | BIGINT | Khối lượng |
| ma5, ma10, ma20, ma30, ma50, ma100, ma200 | DECIMAL(12,2) | Moving Average giá |
| vol_ma5, vol_ma10, vol_ma20, vol_ma30, vol_ma50, vol_ma100, vol_ma200 | BIGINT | Moving Average volume |
| created_at | DATETIME | Thời gian tạo |

---

## Use Cases

### 1. Tìm cổ phiếu breakout mạnh

```
GET /api/v1/score/ranking?ma_period=20&exchange=HOSE&limit=20&sort=desc
```

Tìm top 20 cổ phiếu HOSE có score cao nhất (giá vượt MA20 + volume mạnh).

### 2. Tìm cổ phiếu đang yếu

```
GET /api/v1/score/ranking?ma_period=20&exchange=HOSE&limit=20&sort=asc
```

Tìm 20 cổ phiếu có score thấp nhất (giá dưới MA20).

### 3. Theo dõi momentum của một cổ phiếu

```
GET /api/v1/score/history/VCB?ma_period=20&range=month
```

Xem diễn biến score của VCB trong 1 tháng qua để đánh giá xu hướng.

### 4. So sánh các timeframe

```
GET /api/v1/score/ranking?ma_period=5&limit=10   # Ngắn hạn
GET /api/v1/score/ranking?ma_period=20&limit=10  # Trung hạn
GET /api/v1/score/ranking?ma_period=50&limit=10  # Dài hạn
```

---

## Error Codes

| Status | Description |
|--------|-------------|
| 200 | Success |
| 422 | Validation error (invalid parameters) |
| 500 | Server error |

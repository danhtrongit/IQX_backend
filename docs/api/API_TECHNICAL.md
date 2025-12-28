# Technical Analysis API

API phân tích kỹ thuật - các chỉ báo kỹ thuật, MA, RSI, MACD, Pivot Points.

**Base URL:** `/api/v1/technical`

**Tag:** `Technical Analysis`

---

## Endpoints

### 1. Get Technical Analysis - Phân tích kỹ thuật

```
GET /api/v1/technical/{symbol}
```

Lấy phân tích kỹ thuật đầy đủ cho một mã cổ phiếu.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | string | Mã cổ phiếu |

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `timeframe` | string | `ONE_DAY` | Khung thời gian: `ONE_HOUR`, `ONE_DAY`, `ONE_WEEK` |

#### Response

```json
{
  "symbol": "VNM",
  "timeframe": "ONE_DAY",
  "data": {
    "symbol": "VNM",
    "timeframe": "ONE_DAY",
    "price": 61500,
    "matchTime": "2025-12-26T14:45:00",
    "gaugeSummary": {
      "rating": "NEUTRAL",
      "values": {
        "BUY": 8,
        "NEUTRAL": 8,
        "SELL": 8
      }
    },
    "gaugeMovingAverage": {
      "rating": "BAD",
      "values": {
        "BUY": 4,
        "NEUTRAL": 2,
        "SELL": 6
      }
    },
    "gaugeOscillator": {
      "rating": "NEUTRAL",
      "values": {
        "BUY": 4,
        "NEUTRAL": 6,
        "SELL": 2
      }
    },
    "movingAverages": [
      {"name": "sma5", "rating": "BUY", "value": 61200.0},
      {"name": "sma10", "rating": "BUY", "value": 60800.0},
      {"name": "sma20", "rating": "SELL", "value": 62000.0},
      {"name": "sma50", "rating": "BUY", "value": 60696.0},
      {"name": "sma100", "rating": "BUY", "value": 59500.0},
      {"name": "sma200", "rating": "BUY", "value": 58000.0},
      {"name": "ema5", "rating": "BUY", "value": 61300.0},
      {"name": "ema10", "rating": "BUY", "value": 60900.0},
      {"name": "ema20", "rating": "SELL", "value": 62100.0},
      {"name": "ema50", "rating": "BUY", "value": 60800.0},
      {"name": "vwma", "rating": "BUY", "value": 61100.0}
    ],
    "oscillators": [
      {"name": "rsi", "rating": "NEUTRAL", "value": 48.5},
      {"name": "macd", "rating": "SELL", "value": -150.0},
      {"name": "macdSignal", "rating": null, "value": -100.0},
      {"name": "stochastic", "rating": "NEUTRAL", "value": 55.2},
      {"name": "stochasticRsi", "rating": "NEUTRAL", "value": 45.5},
      {"name": "cci", "rating": "NEUTRAL", "value": -25.8},
      {"name": "adx", "rating": "NEUTRAL", "value": 18.5},
      {"name": "williamsR", "rating": "NEUTRAL", "value": -45.0},
      {"name": "ultimateOscillator", "rating": "NEUTRAL", "value": 50.3}
    ],
    "pivot": {
      "pivotPoint": 61500,
      "resistance1": 62000,
      "resistance2": 62700,
      "resistance3": 63200,
      "support1": 61000,
      "support2": 60300,
      "support3": 59800,
      "fibResistance1": 61800,
      "fibResistance2": 62100,
      "fibResistance3": 62600,
      "fibSupport1": 61200,
      "fibSupport2": 60900,
      "fibSupport3": 60400,
      "camarillaResistance1": 61600,
      "camarillaResistance2": 61700,
      "camarillaResistance3": 61900,
      "camarillaSupport1": 61400,
      "camarillaSupport2": 61300,
      "camarillaSupport3": 61100,
      "woodieResistance1": 62100,
      "woodieResistance2": 62800,
      "woodieSupport1": 60900,
      "woodieSupport2": 60200,
      "woodiePivot": 61400,
      "demarkHigh": 62200,
      "demarkLow": 60800,
      "demarkPivot": 61500
    }
  },
  "error": null
}
```

**Lưu ý quan trọng:**
- Indicator names trả về dạng lowercase (sma5, ema10, rsi thay vì SMA5, EMA10, RSI14)
- Giá trị giá theo đơn vị VND thực (61500 = 61,500 VND)

---

## Data Structure

### Gauge Summary

Tổng hợp tín hiệu mua/bán dựa trên tất cả các chỉ báo.

| Rating | Description |
|--------|-------------|
| `VERY_GOOD` | Tín hiệu mua rất mạnh |
| `GOOD` | Tín hiệu mua |
| `NEUTRAL` | Trung lập |
| `BAD` | Tín hiệu bán |
| `VERY_BAD` | Tín hiệu bán rất mạnh |

### Moving Averages

Các đường trung bình động:

| Indicator | Description |
|-----------|-------------|
| `sma5/10/20/50/100/200` | Simple Moving Average (5, 10, 20, 50, 100, 200 phiên) |
| `ema5/10/20/50` | Exponential Moving Average |
| `vwma` | Volume Weighted Moving Average |

**Rating logic:**
- `BUY`: Giá > MA
- `SELL`: Giá < MA
- `NEUTRAL`: Giá ~ MA (trong biên độ nhỏ)

### Oscillators

Các chỉ báo dao động:

| Indicator | Description | Range |
|-----------|-------------|-------|
| `rsi` | Relative Strength Index (14 phiên) | 0-100 |
| `macd` | Moving Average Convergence Divergence | - |
| `macdSignal` | MACD Signal Line | - |
| `stochastic` | Stochastic Oscillator | 0-100 |
| `stochasticRsi` | Stochastic RSI | 0-100 |
| `cci` | Commodity Channel Index | - |
| `adx` | Average Directional Index | 0-100 |
| `williamsR` | Williams Percent Range | -100 to 0 |
| `ultimateOscillator` | Ultimate Oscillator | 0-100 |

**RSI Rating:**
- `BUY`: RSI < 30 (quá bán)
- `SELL`: RSI > 70 (quá mua)
- `NEUTRAL`: 30 <= RSI <= 70

### Pivot Points

Các mức hỗ trợ/kháng cự:

| Type | Description |
|------|-------------|
| **Classic Pivot** | Pivot Point truyền thống |
| **Fibonacci** | Pivot Points dựa trên Fibonacci retracement |
| **Camarilla** | Camarilla Pivot Points (trading trong ngày) |
| **Woodie** | Woodie Pivot Points |
| **DeMark** | DeMark Pivot Points |

Mỗi loại có:
- `pivotPoint`: Điểm pivot chính
- `resistance1/2/3`: Các mức kháng cự (R1, R2, R3)
- `support1/2/3`: Các mức hỗ trợ (S1, S2, S3)

---

## Timeframes

| Timeframe | Description | Use Case |
|-----------|-------------|----------|
| `ONE_HOUR` | 1 giờ | Scalping, day trading |
| `ONE_DAY` | 1 ngày | Swing trading |
| `ONE_WEEK` | 1 tuần | Position trading, đầu tư |

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 503 | Service Unavailable - Không lấy được dữ liệu từ nguồn |

---

## Caching

| Data Type | Cache TTL |
|-----------|-----------|
| Technical Analysis | 5 phút |

---

## Code Examples

### cURL

```bash
# Get daily technical analysis
curl -X GET "http://localhost:8000/api/v1/technical/VNM?timeframe=ONE_DAY"

# Get hourly technical analysis
curl -X GET "http://localhost:8000/api/v1/technical/FPT?timeframe=ONE_HOUR"

# Get weekly technical analysis
curl -X GET "http://localhost:8000/api/v1/technical/VCB?timeframe=ONE_WEEK"
```

### JavaScript/TypeScript

```typescript
// Get daily technical analysis
const technical = await fetch(
  '/api/v1/technical/VNM?timeframe=ONE_DAY'
).then(r => r.json());

// Access gauge summary
console.log(`Signal: ${technical.data.gaugeSummary.rating}`);
console.log(`Buy signals: ${technical.data.gaugeSummary.values.BUY}`);
console.log(`Sell signals: ${technical.data.gaugeSummary.values.SELL}`);

// Access RSI (note: lowercase name)
const rsi = technical.data.oscillators.find(o => o.name === 'rsi');
console.log(`RSI: ${rsi.value} (${rsi.rating})`);

// Access Pivot Points
const { pivot } = technical.data;
console.log(`Pivot: ${pivot.pivotPoint}`);
console.log(`Resistance 1: ${pivot.resistance1}`);
console.log(`Support 1: ${pivot.support1}`);

// Check if bullish or bearish
const bullishMAs = technical.data.movingAverages.filter(ma => ma.rating === 'BUY');
const bearishMAs = technical.data.movingAverages.filter(ma => ma.rating === 'SELL');
console.log(`Bullish MAs: ${bullishMAs.length}, Bearish MAs: ${bearishMAs.length}`);
```

### Python

```python
import httpx

# Get daily technical analysis
response = httpx.get(
    "http://localhost:8000/api/v1/technical/VNM",
    params={"timeframe": "ONE_DAY"}
)
technical = response.json()

# Access gauge summary
data = technical["data"]
summary = data["gaugeSummary"]
print(f"Signal: {summary['rating']}")
print(f"Buy: {summary['values']['BUY']}, Sell: {summary['values']['SELL']}")

# Access RSI (note: lowercase name)
rsi = next((o for o in data["oscillators"] if o["name"] == "rsi"), None)
if rsi:
    print(f"RSI: {rsi['value']} ({rsi['rating']})")

# Access Pivot Points
pivot = data["pivot"]
print(f"Pivot: {pivot['pivotPoint']}")
print(f"R1: {pivot['resistance1']}, S1: {pivot['support1']}")

# Count bullish vs bearish MAs
bullish = sum(1 for ma in data["movingAverages"] if ma["rating"] == "BUY")
bearish = sum(1 for ma in data["movingAverages"] if ma["rating"] == "SELL")
print(f"Bullish MAs: {bullish}, Bearish MAs: {bearish}")
```

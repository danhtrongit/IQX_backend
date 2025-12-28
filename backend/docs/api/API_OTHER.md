# Other APIs

APIs khác - Chat (Mr.Arix AI), Cache Management, Listing.

---

# Chat API - Mr.Arix

API trò chuyện với AI Assistant chuyên về chứng khoán.

**Base URL:** `/api/v1/chat`

**Tag:** `Chat - Mr.Arix`

---

## Endpoints

### 1. Chat - Trò chuyện với Mr.Arix

```
POST /api/v1/chat
```

Gửi câu hỏi và nhận câu trả lời từ Mr.Arix - Chuyên gia thông tin chứng khoán IQX.

#### Request Body

```json
{
  "message": "Giá VNM hiện tại bao nhiêu?",
  "conversation_id": "conv_123456"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | Câu hỏi của người dùng |
| `conversation_id` | string | No | ID cuộc hội thoại (để duy trì ngữ cảnh) |

#### Response

```json
{
  "response": "Giá VNM (Vinamilk) hiện tại là 85,000 VND, tăng 500 VND (+0.59%) so với phiên trước.\n\nThông tin chi tiết:\n- Giá mở cửa: 84,500\n- Giá cao nhất: 86,000\n- Giá thấp nhất: 84,000\n- Khối lượng: 1,250,000 CP",
  "conversation_id": "conv_123456",
  "sources": ["price_stream", "quotes"],
  "timestamp": "2024-01-15T14:45:00Z"
}
```

#### Example Questions

- "Giá VNM hiện tại bao nhiêu?"
- "Cho tôi thông tin về công ty Vinamilk"
- "Cổ đông lớn của FPT là ai?"
- "PE, PB của VCB là bao nhiêu?"
- "Top 5 cổ phiếu tăng mạnh nhất hôm nay"
- "Khối ngoại đang mua ròng những mã nào?"
- "Báo cáo tài chính quý gần nhất của HPG"

---

### 2. Get Info - Thông tin về Mr.Arix

```
GET /api/v1/chat/info
```

Lấy thông tin về Mr.Arix và các khả năng của AI.

#### Response

```json
{
  "name": "Mr.Arix",
  "role": "Chuyên gia thông tin chứng khoán IQX",
  "capabilities": [
    "Tra cứu giá cổ phiếu realtime",
    "Thông tin công ty (giới thiệu, lịch sử, ngành nghề)",
    "Danh sách cổ đông lớn",
    "Ban lãnh đạo, HĐQT",
    "Báo cáo tài chính (CĐKT, KQKD, LCTT)",
    "Chỉ số tài chính (PE, PB, ROE, ROA, EPS, BVPS)",
    "Tin tức và sự kiện công ty",
    "Top cổ phiếu tăng/giảm/khối lượng/giá trị",
    "Giao dịch khối ngoại",
    "Chỉ số thị trường (VNINDEX, VN30, HNX, UPCOM)",
    "Lịch sử giá cổ phiếu"
  ],
  "disclaimer": "Mr.Arix chỉ cung cấp thông tin, KHÔNG tư vấn đầu tư, KHÔNG khuyến nghị mua/bán.",
  "supported_symbols": "Tất cả mã trên HOSE, HNX, UPCOM"
}
```

---

# Cache API

API quản lý cache hệ thống.

**Base URL:** `/api/v1/cache`

**Tag:** `Cache`

---

## Endpoints

### 1. Get Cache Stats - Thống kê cache

```
GET /api/v1/cache/stats
```

Lấy thống kê sử dụng cache.

#### Response

```json
{
  "entries": 31,
  "hits": 5,
  "misses": 33,
  "sets": 33,
  "hit_rate": "13.2%"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `entries` | int | Số entry đang cache |
| `hits` | int | Số lần cache hit |
| `misses` | int | Số lần cache miss |
| `sets` | int | Số lần set cache |
| `hit_rate` | string | Tỷ lệ hit (%) - trả về dạng string với % |

**Lưu ý:** `hit_rate` trả về dạng string (ví dụ: "13.2%")

---

### 2. Get TTL Config - Cấu hình TTL

```
GET /api/v1/cache/ttl-config
```

Lấy cấu hình TTL (Time-To-Live) của các loại dữ liệu.

#### Response

```json
{
  "realtime": 5,
  "market_overview": 10,
  "price_board": 5,
  "intraday": 10,
  "top_stocks": 300,
  "historical_recent": 300,
  "historical_old": 3600,
  "company_info": 3600,
  "financials": 21600,
  "symbol_list": 3600,
  "industries": 86400,
  "company_overview": 86400,
  "officers": 86400
}
```

*Tất cả giá trị đơn vị là giây (seconds)*

---

### 3. Clear Cache - Xóa cache

```
DELETE /api/v1/cache/clear
```

Xóa cache entries. **Yêu cầu xác thực.**

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pattern` | string | null | Prefix của cache key cần xóa. Để trống = xóa tất cả |

#### Response (xóa theo pattern)

```json
{
  "cleared": true,
  "pattern": "market:",
  "deleted_count": 25
}
```

#### Response (xóa tất cả)

```json
{
  "cleared": true,
  "pattern": "all",
  "message": "All cache entries cleared"
}
```

---

### 4. Delete Cache Key - Xóa một key cụ thể

```
DELETE /api/v1/cache/key/{key}
```

Xóa một cache key cụ thể. **Yêu cầu xác thực.**

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `key` | string | Cache key cần xóa |

#### Response

```json
{
  "key": "quotes:VNM:history",
  "deleted": true
}
```

---

# Listing API

API danh sách chứng khoán niêm yết.

**Base URL:** `/api/v1/listing`

**Tag:** `Listing`

---

## Endpoints

### 1. Get Stocks - Danh sách cổ phiếu

```
GET /api/v1/listing/stocks
```

Lấy danh sách tất cả mã cổ phiếu.

#### Response

```json
{
  "count": 3181,
  "data": [
    {
      "symbol": "YTC",
      "exchange": "UPCOM",
      "type": "STOCK",
      "organ_short_name": "XNK Y tế TP.HCM",
      "organ_name": "Công ty Cổ phần Xuất nhập khẩu Y tế Thành phố Hồ Chí Minh",
      "product_grp_id": "UPX"
    },
    {
      "symbol": "VNM",
      "exchange": "HSX",
      "type": "STOCK",
      "organ_short_name": "VINAMILK",
      "organ_name": "Công ty Cổ phần Sữa Việt Nam",
      "product_grp_id": "HSX"
    },
    {
      "symbol": "FPT",
      "exchange": "HSX",
      "type": "STOCK",
      "organ_short_name": "FPT",
      "organ_name": "Công ty Cổ phần FPT",
      "product_grp_id": "HSX"
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Mã cổ phiếu |
| `exchange` | string | Sàn giao dịch (HSX, HNX, UPCOM) |
| `type` | string | Loại chứng khoán |
| `organ_short_name` | string | Tên viết tắt công ty |
| `organ_name` | string | Tên đầy đủ công ty |
| `product_grp_id` | string | Mã nhóm sản phẩm |

---

### 2. Get ETFs - Danh sách quỹ ETF

```
GET /api/v1/listing/etfs
```

Lấy danh sách tất cả quỹ ETF.

#### Response

```json
{
  "data": [
    {"symbol": "E1VFVN30", "name": "VFMVN30 ETF", "exchange": "HOSE"},
    {"symbol": "FUEVFVND", "name": "VFM VN Diamond ETF", "exchange": "HOSE"},
    {"symbol": "FUESSV50", "name": "SSIAM VNX50 ETF", "exchange": "HOSE"}
  ],
  "count": 15
}
```

---

### 3. Get Industries - Danh sách ngành

```
GET /api/v1/listing/industries
```

Lấy danh sách phân ngành.

#### Response

```json
{
  "data": [
    {"code": "0001", "name": "Dầu khí", "stock_count": 15},
    {"code": "1000", "name": "Nguyên vật liệu", "stock_count": 85},
    {"code": "2000", "name": "Công nghiệp", "stock_count": 120},
    {"code": "3000", "name": "Hàng tiêu dùng", "stock_count": 95},
    {"code": "4000", "name": "Y tế", "stock_count": 25},
    {"code": "5000", "name": "Tiện ích công cộng", "stock_count": 35},
    {"code": "6000", "name": "Tài chính", "stock_count": 85},
    {"code": "7000", "name": "Công nghệ thông tin", "stock_count": 45},
    {"code": "8000", "name": "Dịch vụ viễn thông", "stock_count": 15},
    {"code": "9000", "name": "Bất động sản", "stock_count": 110}
  ],
  "count": 10
}
```

---

### 4. Get Industries ICB - Phân ngành ICB

```
GET /api/v1/listing/industries/icb
```

Lấy phân ngành theo chuẩn ICB (Industry Classification Benchmark).

#### Response

```json
{
  "data": [
    {
      "icb_code": "0001",
      "name": "Dầu khí",
      "english_name": "Oil & Gas",
      "level": 1,
      "parent_code": null
    },
    {
      "icb_code": "0530",
      "name": "Dầu khí - Khoan & Khai thác",
      "english_name": "Oil & Gas Producers",
      "level": 2,
      "parent_code": "0001"
    }
  ],
  "count": 50
}
```

---

## Caching

| Endpoint | Cache TTL |
|----------|-----------|
| Stocks | 24 giờ |
| ETFs | 24 giờ |
| Industries | 24 giờ |
| Industries ICB | 24 giờ |

---

## Code Examples

### cURL

```bash
# Chat with Mr.Arix
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Giá VNM hiện tại bao nhiêu?"}'

# Get Mr.Arix info
curl -X GET http://localhost:8000/api/v1/chat/info

# Get cache stats
curl -X GET http://localhost:8000/api/v1/cache/stats

# Get TTL config
curl -X GET http://localhost:8000/api/v1/cache/ttl-config

# Clear cache (requires auth)
curl -X DELETE "http://localhost:8000/api/v1/cache/clear?pattern=market:" \
  -H "Authorization: Bearer <token>"

# Get stocks
curl -X GET http://localhost:8000/api/v1/listing/stocks

# Get ETFs
curl -X GET http://localhost:8000/api/v1/listing/etfs

# Get industries
curl -X GET http://localhost:8000/api/v1/listing/industries

# Get ICB classification
curl -X GET http://localhost:8000/api/v1/listing/industries/icb
```

### JavaScript/TypeScript

```typescript
// Chat with Mr.Arix
const chat = await fetch('/api/v1/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'Giá VNM hiện tại bao nhiêu?' })
}).then(r => r.json());
console.log(chat.response);

// Get Mr.Arix info
const info = await fetch('/api/v1/chat/info').then(r => r.json());

// Get cache stats
const cacheStats = await fetch('/api/v1/cache/stats').then(r => r.json());
console.log(`Hit rate: ${cacheStats.hit_rate}`);

// Get all stocks
const stocks = await fetch('/api/v1/listing/stocks').then(r => r.json());
console.log(`Total stocks: ${stocks.count}`);

// Get ETFs
const etfs = await fetch('/api/v1/listing/etfs').then(r => r.json());

// Get industries
const industries = await fetch('/api/v1/listing/industries').then(r => r.json());
```

### Python

```python
import httpx

# Chat with Mr.Arix
chat = httpx.post(
    "http://localhost:8000/api/v1/chat",
    json={"message": "Giá VNM hiện tại bao nhiêu?"}
).json()
print(chat["response"])

# Get Mr.Arix info
info = httpx.get("http://localhost:8000/api/v1/chat/info").json()

# Get cache stats
cache_stats = httpx.get("http://localhost:8000/api/v1/cache/stats").json()
print(f"Hit rate: {cache_stats['hit_rate']}")

# Get all stocks
stocks = httpx.get("http://localhost:8000/api/v1/listing/stocks").json()
print(f"Total stocks: {stocks['count']}")

# Get ETFs
etfs = httpx.get("http://localhost:8000/api/v1/listing/etfs").json()

# Get industries
industries = httpx.get("http://localhost:8000/api/v1/listing/industries").json()

# Get ICB classification
icb = httpx.get("http://localhost:8000/api/v1/listing/industries/icb").json()
```

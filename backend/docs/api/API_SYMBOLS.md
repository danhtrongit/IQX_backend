# Symbols API

API quản lý danh sách mã cổ phiếu - tìm kiếm, lọc, phân loại ngành.

**Base URL:** `/api/v1/symbols`

**Tag:** `Symbols`

---

## Endpoints

### 1. List Symbols - Danh sách mã cổ phiếu

```
GET /api/v1/symbols
```

Lấy danh sách tất cả mã cổ phiếu với bộ lọc.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `exchange` | string | null | Lọc theo sàn: `HOSE`, `HNX`, `UPCOM` |
| `type` | string | null | Lọc theo loại: `STOCK`, `ETF`, `CW`, `BOND` |
| `icb_code2` | string | null | Lọc theo mã ngành ICB cấp 2 |
| `is_active` | boolean | true | Chỉ lấy mã đang giao dịch |
| `limit` | int | 100 | Số kết quả (1-1000) |
| `offset` | int | 0 | Vị trí bắt đầu |

#### Response

```json
{
  "items": [
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
  ],
  "total": 500,
  "limit": 100,
  "offset": 0
}
```

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Mã cổ phiếu |
| `exchange` | string | Sàn giao dịch (HSX, HNX, UPCOM) |
| `type` | string | Loại chứng khoán (STOCK, ETF, CW, BOND) |
| `organ_short_name` | string | Tên viết tắt công ty |
| `organ_name` | string | Tên đầy đủ công ty |
| `product_grp_id` | string | Mã nhóm sản phẩm |

---

### 2. Search Symbols - Tìm kiếm mã

```
GET /api/v1/symbols/search
```

Tìm kiếm mã cổ phiếu theo tên hoặc mã.

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Từ khóa tìm kiếm (1-50 ký tự) |
| `limit` | int | No | Số kết quả (1-100), mặc định: 20 |

#### Response

```json
[
  {
    "symbol": "VNM",
    "organ_name": "Công ty Cổ phần Sữa Việt Nam",
    "organ_short_name": "VINAMILK",
    "exchange": "HSX",
    "type": "STOCK"
  },
  {
    "symbol": "VNS",
    "organ_name": "Công ty Cổ phần Ánh Dương Việt Nam",
    "organ_short_name": "VINASUN",
    "exchange": "HSX",
    "type": "STOCK"
  }
]
```

---

### 3. List Industries - Danh sách ngành ICB

```
GET /api/v1/symbols/industries
```

Lấy danh sách phân ngành theo chuẩn ICB.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | int | null | Cấp độ ICB (1-4) |

#### Response

```json
{
  "data": [
    {
      "icb_code": "0001",
      "name": "Dầu khí",
      "english_name": "Oil & Gas",
      "level": 1,
      "parent_code": null,
      "stock_count": 15
    },
    {
      "icb_code": "0530",
      "name": "Dầu khí - Khoan & Khai thác",
      "english_name": "Oil & Gas Producers",
      "level": 2,
      "parent_code": "0001",
      "stock_count": 8
    },
    {
      "icb_code": "1000",
      "name": "Nguyên vật liệu",
      "english_name": "Basic Materials",
      "level": 1,
      "parent_code": null,
      "stock_count": 85
    }
  ],
  "count": 50
}
```

#### ICB Levels

| Level | Description | Example |
|-------|-------------|---------|
| 1 | Industry (Ngành) | Dầu khí, Tài chính |
| 2 | Supersector | Ngân hàng, Bảo hiểm |
| 3 | Sector | Ngân hàng thương mại |
| 4 | Subsector | Ngân hàng bán lẻ |

---

### 4. Get Symbol Detail - Chi tiết mã

```
GET /api/v1/symbols/{symbol}
```

Lấy thông tin chi tiết của một mã cổ phiếu.

#### Response

```json
{
  "id": 87,
  "symbol": "VNM",
  "organ_name": "Công ty Cổ phần Sữa Việt Nam",
  "organ_short_name": "VINAMILK",
  "exchange": "HSX",
  "type": "STOCK",
  "icb_code1": "3000",
  "icb_code2": "3500",
  "icb_code3": "3570",
  "icb_code4": "3577",
  "icb_name2": "Thực phẩm và đồ uống",
  "icb_name3": "Sản xuất thực phẩm",
  "icb_name4": "Thực phẩm",
  "company_profile": "Công ty Cổ phần Sữa Việt Nam (VNM) là một công ty sản xuất, kinh doanh sữa và các sản phẩm từ sữa...",
  "history": "Công ty Cổ phần Sữa Việt Nam (Vinamilk) được thành lập dựa trên quyết định số 155/2003/QĐ-BCN...",
  "issue_share": 2089955445.0,
  "charter_capital": 20899554450000.0,
  "product_grp_id": "HSX"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | number | ID nội bộ |
| `symbol` | string | Mã cổ phiếu |
| `organ_name` | string | Tên đầy đủ công ty |
| `organ_short_name` | string | Tên viết tắt |
| `exchange` | string | Sàn giao dịch |
| `type` | string | Loại chứng khoán |
| `icb_code1/2/3/4` | string | Mã ngành ICB các cấp |
| `icb_name2/3/4` | string | Tên ngành ICB các cấp |
| `company_profile` | string | Mô tả công ty |
| `history` | string | Lịch sử hình thành |
| `issue_share` | number | Số cổ phiếu đã phát hành |
| `charter_capital` | number | Vốn điều lệ (VND) |
| `product_grp_id` | string | Mã nhóm sản phẩm |

---

### 5. Sync Symbols - Đồng bộ dữ liệu

```
POST /api/v1/symbols/sync
```

Đồng bộ danh sách mã từ nguồn dữ liệu (vnstock).

**Yêu cầu xác thực:** Bearer Token

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sync_details` | boolean | false | Đồng bộ cả thông tin chi tiết công ty (chậm hơn) |

#### Response

```json
{
  "synced": 1800,
  "created": 15,
  "updated": 1785,
  "errors": 0,
  "duration_seconds": 45.5,
  "message": "Sync completed successfully"
}
```

---

## Symbol Types

| Type | Description |
|------|-------------|
| `STOCK` | Cổ phiếu |
| `ETF` | Quỹ ETF |
| `CW` | Chứng quyền có đảm bảo |
| `BOND` | Trái phiếu |

---

## Exchanges

| Exchange | Description |
|----------|-------------|
| `HSX` / `HOSE` | Sở Giao dịch Chứng khoán TP.HCM |
| `HNX` | Sở Giao dịch Chứng khoán Hà Nội |
| `UPCOM` | Sàn giao dịch UPCoM |

**Lưu ý:** API trả về `HSX` thay vì `HOSE`

---

## Caching

| Data Type | Cache TTL |
|-----------|-----------|
| Symbol List | 1 giờ |
| Symbol Search | 1 giờ |
| Industries | 24 giờ |
| Symbol Detail | 1 giờ |

---

## Code Examples

### cURL

```bash
# List all stocks on HOSE
curl -X GET "http://localhost:8000/api/v1/symbols?exchange=HOSE&type=STOCK&limit=50"

# Search symbols
curl -X GET "http://localhost:8000/api/v1/symbols/search?q=vinamilk&limit=10"

# List industries
curl -X GET "http://localhost:8000/api/v1/symbols/industries?level=2"

# Get symbol detail
curl -X GET http://localhost:8000/api/v1/symbols/VNM

# Sync symbols (requires auth)
curl -X POST "http://localhost:8000/api/v1/symbols/sync?sync_details=false" \
  -H "Authorization: Bearer <token>"
```

### JavaScript/TypeScript

```typescript
// List stocks on HOSE
const stocks = await fetch(
  '/api/v1/symbols?exchange=HOSE&type=STOCK&limit=100'
).then(r => r.json());

// Search symbols
const results = await fetch(
  '/api/v1/symbols/search?q=vin&limit=10'
).then(r => r.json());

// Get industries
const industries = await fetch(
  '/api/v1/symbols/industries?level=2'
).then(r => r.json());

// Get symbol detail
const vnm = await fetch('/api/v1/symbols/VNM').then(r => r.json());
```

### Python

```python
import httpx

# List stocks
stocks = httpx.get(
    "http://localhost:8000/api/v1/symbols",
    params={"exchange": "HOSE", "type": "STOCK", "limit": 100}
).json()

# Search symbols
results = httpx.get(
    "http://localhost:8000/api/v1/symbols/search",
    params={"q": "vinamilk", "limit": 10}
).json()

# Get industries
industries = httpx.get(
    "http://localhost:8000/api/v1/symbols/industries",
    params={"level": 2}
).json()

# Get symbol detail
vnm = httpx.get("http://localhost:8000/api/v1/symbols/VNM").json()
```

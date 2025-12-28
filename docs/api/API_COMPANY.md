# Company API

API thông tin doanh nghiệp - tổng quan, cổ đông, ban lãnh đạo, sự kiện, tin tức.

**Base URL:** `/api/v1/company`

**Tag:** `Company`

---

## Endpoints

### 1. Get Overview - Tổng quan công ty

```
GET /api/v1/company/{symbol}/overview
```

Lấy thông tin tổng quan về công ty.

#### Response

```json
{
  "symbol": "VNM",
  "company_profile": "Công ty Cổ phần Sữa Việt Nam (VNM) là một công ty sản xuất, kinh doanh sữa và các sản phẩm từ sữa, cũng như các thiết bị máy móc liên quan ngành sữa tại Việt Nam...",
  "history": "Công ty Cổ phần Sữa Việt Nam (Vinamilk) được thành lập dựa trên quyết định số 155/2003/QĐ-BCN ngày 01/10/2003 của Bộ Công nghiệp về việc chuyển Doanh nghiệp Nhà nước...",
  "icb_name2": "Thực phẩm và đồ uống",
  "icb_name3": "Sản xuất thực phẩm",
  "icb_name4": "Thực phẩm",
  "issue_share": 2089955445.0,
  "charter_capital": 20899554450000.0
}
```

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Mã cổ phiếu |
| `company_profile` | string | Mô tả công ty |
| `history` | string | Lịch sử hình thành |
| `icb_name2` | string | Ngành ICB cấp 2 |
| `icb_name3` | string | Ngành ICB cấp 3 |
| `icb_name4` | string | Ngành ICB cấp 4 |
| `issue_share` | number | Số cổ phiếu đã phát hành |
| `charter_capital` | number | Vốn điều lệ (VND) |

---

### 2. Get Shareholders - Cổ đông lớn

```
GET /api/v1/company/{symbol}/shareholders
```

Lấy danh sách cổ đông lớn của công ty.

#### Response

```json
{
  "symbol": "VNM",
  "data": [
    {
      "share_holder": "Tổng Công ty Đầu Tư Và Kinh Doanh Vốn Nhà Nước",
      "share_own_percent": 0.36,
      "update_date": "2025-10-05"
    },
    {
      "share_holder": "Vietnam Enterprise Investments Limited (VEIL)",
      "share_own_percent": 0.0,
      "update_date": "2025-10-05"
    },
    {
      "share_holder": "F&N Dairy Investments Pte. Ltd.",
      "share_own_percent": 0.17,
      "update_date": "2025-10-05"
    }
  ],
  "count": 3
}
```

| Field | Type | Description |
|-------|------|-------------|
| `share_holder` | string | Tên cổ đông |
| `share_own_percent` | number | Tỷ lệ sở hữu (dạng decimal, 0.36 = 36%) |
| `update_date` | string | Ngày cập nhật (YYYY-MM-DD) |

**Lưu ý:** Tỷ lệ sở hữu trả về dưới dạng decimal (0.36 = 36%)

---

### 3. Get Officers - Ban lãnh đạo

```
GET /api/v1/company/{symbol}/officers
```

Lấy danh sách ban lãnh đạo, HĐQT.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filter_by` | string | `working` | Lọc: `working` (đang làm), `resigned` (đã nghỉ), `all` |

#### Response

```json
{
  "symbol": "VNM",
  "data": [
    {
      "officer_name": "Mai Kiều Liên",
      "officer_position": "Phụ trách Công bố thông tin/Tổng Giám đốc/Thành viên Hội đồng Quản trị",
      "officer_own_percent": 0.0031,
      "update_date": "2025-08-14"
    },
    {
      "officer_name": "Lê Thành Liêm",
      "officer_position": "Giám đốc điều hành Tài Chính",
      "officer_own_percent": 0.0006,
      "update_date": "2025-08-14"
    }
  ],
  "count": 2
}
```

| Field | Type | Description |
|-------|------|-------------|
| `officer_name` | string | Tên thành viên |
| `officer_position` | string | Chức vụ |
| `officer_own_percent` | number | Tỷ lệ sở hữu (dạng decimal, 0.0031 = 0.31%) |
| `update_date` | string | Ngày cập nhật (YYYY-MM-DD) |

---

### 4. Get Events - Sự kiện công ty

```
GET /api/v1/company/{symbol}/events
```

Lấy danh sách sự kiện của công ty (ĐHCĐ, trả cổ tức, niêm yết thêm...).

#### Response

```json
{
  "symbol": "VNM",
  "events": [
    {
      "id": 1,
      "title": "Đại hội đồng cổ đông thường niên 2024",
      "event_type": "SHAREHOLDER_MEETING",
      "event_date": "2024-04-20",
      "description": "Họp ĐHĐCĐ thường niên năm 2024",
      "venue": "Khách sạn Rex, TP.HCM",
      "created_at": "2024-03-15"
    },
    {
      "id": 2,
      "title": "Chốt danh sách cổ đông nhận cổ tức",
      "event_type": "DIVIDEND",
      "event_date": "2024-03-25",
      "description": "Cổ tức năm 2023: 1,500 VND/cổ phiếu",
      "ex_date": "2024-03-24",
      "payment_date": "2024-04-15",
      "created_at": "2024-03-01"
    }
  ],
  "count": 2
}
```

#### Event Types

| Type | Description |
|------|-------------|
| `SHAREHOLDER_MEETING` | Đại hội cổ đông |
| `DIVIDEND` | Trả cổ tức |
| `STOCK_SPLIT` | Chia tách cổ phiếu |
| `BONUS_SHARES` | Thưởng cổ phiếu |
| `RIGHTS_ISSUE` | Phát hành quyền mua |
| `OTHER` | Sự kiện khác |

---

### 5. Get News - Tin tức công ty

```
GET /api/v1/company/{symbol}/news
```

Lấy tin tức liên quan đến công ty.

#### Response

```json
{
  "symbol": "VNM",
  "news": [
    {
      "id": 1,
      "title": "Vinamilk công bố kết quả kinh doanh quý 4/2023",
      "summary": "Doanh thu đạt 15,000 tỷ đồng, tăng 8% so với cùng kỳ...",
      "source": "CafeF",
      "url": "https://cafef.vn/...",
      "published_at": "2024-01-20T10:30:00Z"
    },
    {
      "id": 2,
      "title": "Vinamilk mở rộng thị trường xuất khẩu",
      "summary": "Công ty đặt mục tiêu xuất khẩu chiếm 20% doanh thu...",
      "source": "VnExpress",
      "url": "https://vnexpress.net/...",
      "published_at": "2024-01-18T14:00:00Z"
    }
  ],
  "count": 2
}
```

---

### 6. Get Stock Detail - Chi tiết cổ phiếu

```
GET /api/v1/company/{symbol}/detail
```

Lấy thông tin chi tiết cổ phiếu cho trang stock detail.

#### Response

```json
{
  "symbol": "VNM",
  "company_name": "Công ty Cổ phần Sữa Việt Nam",
  "exchange": "HOSE",
  "industry": "Thực phẩm & Đồ uống",
  "price": {
    "current": 85000,
    "change": 1500,
    "change_percent": 1.80,
    "open": 83500,
    "high": 85500,
    "low": 83000,
    "ceiling": 89500,
    "floor": 77500,
    "ref": 83500
  },
  "trading": {
    "volume": 1250000,
    "value": 106250000000,
    "avg_volume_10d": 980000,
    "avg_volume_20d": 1050000
  },
  "valuation": {
    "market_cap": 177598571645000,
    "pe": 18.5,
    "pb": 4.2,
    "eps": 4594,
    "book_value": 20238
  },
  "profile": {
    "listing_date": "2006-01-19",
    "outstanding_shares": 2089396137,
    "foreign_limit": 49.00,
    "foreign_current": 48.50
  }
}
```

---

### 7. Get Analysis Reports - Báo cáo phân tích

```
GET /api/v1/company/{symbol}/analysis-reports
```

Lấy các báo cáo phân tích từ công ty chứng khoán.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 0 | Trang (0-indexed) |
| `size` | int | 20 | Số báo cáo mỗi trang (1-100) |

#### Response

```json
{
  "symbol": "VNM",
  "reports": [
    {
      "id": 1,
      "title": "Vinamilk - Khuyến nghị Mua với giá mục tiêu 95,000",
      "source": "SSI Research",
      "recommendation": "BUY",
      "target_price": 95000,
      "published_date": "2024-01-15",
      "download_url": "https://..."
    },
    {
      "id": 2,
      "title": "Vinamilk - Triển vọng tăng trưởng 2024",
      "source": "VCSC",
      "recommendation": "HOLD",
      "target_price": 88000,
      "published_date": "2024-01-10",
      "download_url": "https://..."
    }
  ],
  "total": 25,
  "page": 0,
  "size": 20
}
```

---

## Caching

| Data Type | Cache TTL |
|-----------|-----------|
| Company Overview | 24 giờ |
| Shareholders | 24 giờ |
| Officers | 24 giờ |
| Events | 30 phút |
| News | 5 phút |
| Stock Detail | 10 giây |
| Analysis Reports | 6 giờ |

---

## Code Examples

### cURL

```bash
# Get company overview
curl -X GET http://localhost:8000/api/v1/company/VNM/overview

# Get shareholders
curl -X GET http://localhost:8000/api/v1/company/VNM/shareholders

# Get officers (working only)
curl -X GET "http://localhost:8000/api/v1/company/VNM/officers?filter_by=working"

# Get events
curl -X GET http://localhost:8000/api/v1/company/VNM/events

# Get news
curl -X GET http://localhost:8000/api/v1/company/VNM/news

# Get stock detail
curl -X GET http://localhost:8000/api/v1/company/VNM/detail

# Get analysis reports
curl -X GET "http://localhost:8000/api/v1/company/VNM/analysis-reports?page=0&size=10"
```

### JavaScript/TypeScript

```typescript
// Get company overview
const overview = await fetch('/api/v1/company/VNM/overview').then(r => r.json());

// Get shareholders
const shareholders = await fetch('/api/v1/company/VNM/shareholders').then(r => r.json());

// Get officers
const officers = await fetch('/api/v1/company/VNM/officers?filter_by=working').then(r => r.json());

// Get stock detail
const detail = await fetch('/api/v1/company/VNM/detail').then(r => r.json());
```

### Python

```python
import httpx

# Get company overview
overview = httpx.get("http://localhost:8000/api/v1/company/VNM/overview").json()

# Get shareholders
shareholders = httpx.get("http://localhost:8000/api/v1/company/VNM/shareholders").json()

# Get officers
officers = httpx.get(
    "http://localhost:8000/api/v1/company/VNM/officers",
    params={"filter_by": "working"}
).json()

# Get stock detail
detail = httpx.get("http://localhost:8000/api/v1/company/VNM/detail").json()
```

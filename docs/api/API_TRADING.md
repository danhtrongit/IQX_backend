# Trading API

API giao dịch chứng khoán (Paper Trading) - mô phỏng giao dịch thực với tiền ảo.

**Base URL:** `/api/v1/trading`

**Tag:** `Trading`

**Yêu cầu xác thực:** Tất cả endpoints yêu cầu Bearer Token

---

## Tổng quan

Trading API cho phép:
- Quản lý ví (wallet) với số dư VND
- Đặt lệnh mua/bán (BUY/SELL)
- Theo dõi vị thế (positions) cổ phiếu
- Xem lịch sử giao dịch (trades)
- Audit trail (ledger) cho tất cả biến động số dư

### Đặc điểm:
- **Paper Trading:** Giao dịch ảo với tiền ảo 1 tỷ VND
- **Phí giao dịch:** 0.1% mỗi lệnh
- **Thanh toán ngay (T+0):** Không có T+2 như thực tế
- **Market/Limit orders:** Hỗ trợ lệnh thị trường và lệnh giới hạn

---

## Endpoints

### 1. Get Wallet - Lấy thông tin ví

```
GET /api/v1/trading/wallet
```

Lấy thông tin số dư ví của user.

#### Response

```json
{
  "balance": "1000000000",
  "locked": "50000000",
  "available": "950000000",
  "currency": "VND",
  "first_grant_at": "2024-01-15T10:30:00Z"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `balance` | string | Tổng số dư |
| `locked` | string | Số tiền bị khóa (đang chờ khớp lệnh) |
| `available` | string | Số dư khả dụng = balance - locked |
| `currency` | string | Đơn vị tiền tệ (VND) |
| `first_grant_at` | string | Thời điểm nhận tiền lần đầu |

---

### 2. Grant Initial Cash - Nhận tiền khởi đầu

```
POST /api/v1/trading/bootstrap/grant-initial-cash
```

Nhận 1 tỷ VND tiền ảo để bắt đầu giao dịch. Chỉ được nhận 1 lần.

#### Response (lần đầu)

```json
{
  "granted": true,
  "message": "Granted 1,000,000,000 VND to your account",
  "wallet": {
    "balance": "1000000000",
    "locked": "0",
    "available": "1000000000",
    "currency": "VND",
    "first_grant_at": "2024-01-15T10:30:00Z"
  }
}
```

#### Response (lần tiếp theo)

```json
{
  "granted": false,
  "message": "Cash already granted to your account",
  "wallet": {
    "balance": "1000000000",
    "locked": "0",
    "available": "1000000000",
    "currency": "VND",
    "first_grant_at": "2024-01-15T10:30:00Z"
  }
}
```

---

### 3. Get Positions - Lấy danh sách vị thế

```
GET /api/v1/trading/positions
```

Lấy danh sách cổ phiếu đang nắm giữ với P&L.

#### Response

```json
{
  "data": [
    {
      "symbol": "VNM",
      "quantity": "100",
      "locked_quantity": "0",
      "available_quantity": "100",
      "avg_price": "85000",
      "market_price": "87000",
      "market_value": "8700000",
      "unrealized_pnl": "200000",
      "unrealized_pnl_percent": "2.35",
      "updated_at": "2024-01-15T14:30:00Z"
    }
  ],
  "total_market_value": "8700000",
  "total_unrealized_pnl": "200000"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Mã cổ phiếu |
| `quantity` | string | Tổng số lượng |
| `locked_quantity` | string | Số lượng đang bị khóa (chờ bán) |
| `available_quantity` | string | Số lượng có thể bán |
| `avg_price` | string | Giá mua trung bình |
| `market_price` | string | Giá thị trường hiện tại |
| `market_value` | string | Giá trị thị trường |
| `unrealized_pnl` | string | Lãi/lỗ chưa thực hiện |
| `unrealized_pnl_percent` | string | % lãi/lỗ |

---

### 4. Place Order - Đặt lệnh

```
POST /api/v1/trading/orders
```

Đặt lệnh mua hoặc bán cổ phiếu.

#### Request Body

```json
{
  "symbol": "VNM",
  "side": "BUY",
  "type": "MARKET",
  "quantity": "100",
  "limit_price": null,
  "client_order_id": "my-order-001"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | string | Yes | Mã cổ phiếu (VNM, FPT, VCB...) |
| `side` | string | Yes | `BUY` hoặc `SELL` |
| `type` | string | Yes | `MARKET` hoặc `LIMIT` |
| `quantity` | string | Yes | Số lượng (> 0) |
| `limit_price` | string | No* | Giá giới hạn (*bắt buộc nếu type=LIMIT) |
| `client_order_id` | string | No | ID tùy chỉnh (max 50 ký tự, unique) |

#### Response (Market Order - Filled)

```json
{
  "order": {
    "id": 1,
    "symbol": "VNM",
    "side": "BUY",
    "type": "MARKET",
    "quantity": "100",
    "filled_quantity": "100",
    "remaining_quantity": "0",
    "limit_price": null,
    "avg_filled_price": "85000",
    "price_snapshot": "85000",
    "fee_total": "8500",
    "status": "FILLED",
    "client_order_id": "my-order-001",
    "created_at": "2024-01-15T10:30:00Z",
    "filled_at": "2024-01-15T10:30:00Z",
    "canceled_at": null
  },
  "wallet": {
    "balance": "991491500",
    "locked": "0",
    "available": "991491500",
    "currency": "VND"
  },
  "trades": [
    {
      "id": 1,
      "order_id": 1,
      "symbol": "VNM",
      "side": "BUY",
      "quantity": "100",
      "price": "85000",
      "value": "8500000",
      "fee": "8500",
      "executed_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Response (Limit Order - Pending)

```json
{
  "order": {
    "id": 2,
    "symbol": "VNM",
    "side": "BUY",
    "type": "LIMIT",
    "quantity": "100",
    "filled_quantity": "0",
    "remaining_quantity": "100",
    "limit_price": "80000",
    "avg_filled_price": null,
    "price_snapshot": "85000",
    "fee_total": "0",
    "status": "NEW",
    "client_order_id": null,
    "created_at": "2024-01-15T10:30:00Z",
    "filled_at": null,
    "canceled_at": null
  },
  "wallet": {
    "balance": "991491500",
    "locked": "8008000",
    "available": "983483500",
    "currency": "VND"
  },
  "trades": []
}
```

#### Order Status

| Status | Description |
|--------|-------------|
| `NEW` | Lệnh mới, chưa khớp |
| `PARTIALLY_FILLED` | Đã khớp một phần |
| `FILLED` | Đã khớp hoàn toàn |
| `CANCELED` | Đã hủy |

#### Errors

| Code | Status | Description |
|------|--------|-------------|
| `INSUFFICIENT_BALANCE` | 400 | Không đủ số dư |
| `INSUFFICIENT_POSITION` | 400 | Không đủ cổ phiếu để bán |
| `INVALID_ORDER` | 400 | Lệnh không hợp lệ (thiếu limit_price) |
| `MARKET_PRICE_NOT_FOUND` | 400 | Không tìm thấy giá thị trường |
| `DUPLICATE_CLIENT_ORDER_ID` | 400 | client_order_id đã tồn tại |

---

### 5. Get Orders - Lấy danh sách lệnh

```
GET /api/v1/trading/orders
```

Lấy lịch sử lệnh với bộ lọc.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | string | null | Lọc theo status (NEW, FILLED, CANCELED) |
| `symbol` | string | null | Lọc theo mã cổ phiếu |
| `limit` | int | 100 | Số lượng kết quả (1-1000) |
| `offset` | int | 0 | Vị trí bắt đầu |

#### Response

```json
{
  "data": [
    {
      "id": 1,
      "symbol": "VNM",
      "side": "BUY",
      "type": "MARKET",
      "quantity": "100",
      "filled_quantity": "100",
      "status": "FILLED",
      "avg_filled_price": "85000",
      "fee_total": "8500",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "count": 1
}
```

---

### 6. Get Order by ID - Lấy chi tiết lệnh

```
GET /api/v1/trading/orders/{order_id}
```

Lấy chi tiết một lệnh theo ID.

#### Response

```json
{
  "order": {
    "id": 1,
    "symbol": "VNM",
    "side": "BUY",
    "type": "MARKET",
    "quantity": "100",
    "filled_quantity": "100",
    "remaining_quantity": "0",
    "limit_price": null,
    "avg_filled_price": "85000",
    "price_snapshot": "85000",
    "fee_total": "8500",
    "status": "FILLED",
    "client_order_id": null,
    "created_at": "2024-01-15T10:30:00Z",
    "filled_at": "2024-01-15T10:30:00Z",
    "canceled_at": null
  },
  "trades": [
    {
      "id": 1,
      "order_id": 1,
      "symbol": "VNM",
      "side": "BUY",
      "quantity": "100",
      "price": "85000",
      "value": "8500000",
      "fee": "8500",
      "executed_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Errors

| Code | Status | Description |
|------|--------|-------------|
| `ORDER_NOT_FOUND` | 400 | Không tìm thấy lệnh |

---

### 7. Cancel Order - Hủy lệnh

```
POST /api/v1/trading/orders/{order_id}/cancel
```

Hủy lệnh đang chờ khớp.

#### Response

```json
{
  "order": {
    "id": 2,
    "symbol": "VNM",
    "side": "BUY",
    "type": "LIMIT",
    "quantity": "100",
    "filled_quantity": "0",
    "status": "CANCELED",
    "canceled_at": "2024-01-15T10:35:00Z"
  },
  "wallet": {
    "balance": "991491500",
    "locked": "0",
    "available": "991491500",
    "currency": "VND"
  }
}
```

#### Errors

| Code | Status | Description |
|------|--------|-------------|
| `ORDER_NOT_FOUND` | 400 | Không tìm thấy lệnh |
| `ORDER_NOT_CANCELABLE` | 400 | Lệnh không thể hủy (đã khớp hoặc đã hủy) |

---

### 8. Get Trades - Lấy lịch sử giao dịch

```
GET /api/v1/trading/trades
```

Lấy danh sách các lệnh đã khớp.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | string | null | Lọc theo mã cổ phiếu |
| `limit` | int | 100 | Số lượng kết quả (1-1000) |
| `offset` | int | 0 | Vị trí bắt đầu |

#### Response

```json
{
  "data": [
    {
      "id": 1,
      "order_id": 1,
      "symbol": "VNM",
      "side": "BUY",
      "quantity": "100",
      "price": "85000",
      "value": "8500000",
      "fee": "8500",
      "executed_at": "2024-01-15T10:30:00Z"
    }
  ],
  "count": 1
}
```

---

### 9. Get Ledger - Lấy nhật ký giao dịch

```
GET /api/v1/trading/ledger
```

Lấy audit trail cho tất cả biến động số dư.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `entry_type` | string | null | Lọc theo loại: GRANT, BUY, SELL, FEE, LOCK, UNLOCK |
| `limit` | int | 100 | Số lượng kết quả (1-1000) |
| `offset` | int | 0 | Vị trí bắt đầu |

#### Response

```json
{
  "data": [
    {
      "id": 1,
      "entry_type": "GRANT",
      "amount": "1000000000",
      "balance_after": "1000000000",
      "ref_type": "SYSTEM",
      "ref_id": null,
      "description": "Initial cash grant",
      "created_at": "2024-01-15T10:00:00Z"
    },
    {
      "id": 2,
      "entry_type": "LOCK",
      "amount": "-8508500",
      "balance_after": "991491500",
      "ref_type": "ORDER",
      "ref_id": 1,
      "description": null,
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 3,
      "entry_type": "BUY",
      "amount": "-8500000",
      "balance_after": "991491500",
      "ref_type": "TRADE",
      "ref_id": 1,
      "description": null,
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 4,
      "entry_type": "FEE",
      "amount": "-8500",
      "balance_after": "991491500",
      "ref_type": "TRADE",
      "ref_id": 1,
      "description": null,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "count": 4
}
```

#### Entry Types

| Type | Description |
|------|-------------|
| `GRANT` | Nhận tiền khởi đầu |
| `BUY` | Mua cổ phiếu |
| `SELL` | Bán cổ phiếu |
| `FEE` | Phí giao dịch |
| `LOCK` | Khóa tiền khi đặt lệnh |
| `UNLOCK` | Mở khóa tiền khi hủy lệnh |

---

## Fee Calculation

**Phí giao dịch:** 0.1% giá trị giao dịch

```
fee = quantity × price × 0.001
```

Ví dụ: Mua 100 cổ VNM giá 85,000 VND
```
Giá trị = 100 × 85,000 = 8,500,000 VND
Phí = 8,500,000 × 0.001 = 8,500 VND
Tổng = 8,508,500 VND
```

---

## Code Examples

### cURL

```bash
# Get wallet
curl -X GET http://localhost:8000/api/v1/trading/wallet \
  -H "Authorization: Bearer <token>"

# Grant cash
curl -X POST http://localhost:8000/api/v1/trading/bootstrap/grant-initial-cash \
  -H "Authorization: Bearer <token>"

# Place market buy order
curl -X POST http://localhost:8000/api/v1/trading/orders \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"VNM","side":"BUY","type":"MARKET","quantity":"100"}'

# Place limit sell order
curl -X POST http://localhost:8000/api/v1/trading/orders \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"VNM","side":"SELL","type":"LIMIT","quantity":"50","limit_price":"90000"}'

# Cancel order
curl -X POST http://localhost:8000/api/v1/trading/orders/1/cancel \
  -H "Authorization: Bearer <token>"

# Get positions
curl -X GET http://localhost:8000/api/v1/trading/positions \
  -H "Authorization: Bearer <token>"
```

### JavaScript/TypeScript

```typescript
const headers = {
  'Authorization': `Bearer ${accessToken}`,
  'Content-Type': 'application/json'
};

// Get wallet
const wallet = await fetch('/api/v1/trading/wallet', { headers }).then(r => r.json());

// Place order
const order = await fetch('/api/v1/trading/orders', {
  method: 'POST',
  headers,
  body: JSON.stringify({
    symbol: 'VNM',
    side: 'BUY',
    type: 'MARKET',
    quantity: '100'
  })
}).then(r => r.json());

// Get positions
const positions = await fetch('/api/v1/trading/positions', { headers }).then(r => r.json());
```

### Python

```python
import httpx

headers = {"Authorization": f"Bearer {access_token}"}

# Get wallet
wallet = httpx.get(
    "http://localhost:8000/api/v1/trading/wallet",
    headers=headers
).json()

# Place order
order = httpx.post(
    "http://localhost:8000/api/v1/trading/orders",
    headers=headers,
    json={
        "symbol": "VNM",
        "side": "BUY",
        "type": "MARKET",
        "quantity": "100"
    }
).json()

# Get positions
positions = httpx.get(
    "http://localhost:8000/api/v1/trading/positions",
    headers=headers
).json()
```

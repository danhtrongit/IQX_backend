# Authentication API

API xác thực người dùng (đăng ký, đăng nhập, refresh token, logout).

**Base URL:** `/api/v1/auth`

**Tag:** `Authentication`

---

## Endpoints

### 1. Register - Đăng ký tài khoản

```
POST /api/v1/auth/register
```

Đăng ký tài khoản người dùng mới.

#### Request Body

```json
{
  "email": "user@example.com",
  "password": "Password123",
  "fullname": "Nguyễn Văn A"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | Email đăng ký (unique) |
| `password` | string | Yes | Mật khẩu (min 8 ký tự, có chữ hoa, chữ thường, số) |
| `fullname` | string | Yes | Họ tên người dùng |

#### Response

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "fullname": "Nguyễn Văn A",
    "role": "USER",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  },
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

#### Errors

| Code | Status | Description |
|------|--------|-------------|
| `EMAIL_EXISTS` | 409 | Email đã được đăng ký |
| `VALIDATION_ERROR` | 422 | Dữ liệu không hợp lệ |

---

### 2. Login - Đăng nhập

```
POST /api/v1/auth/login
```

Đăng nhập bằng email và password.

#### Request Body

```json
{
  "email": "user@example.com",
  "password": "Password123"
}
```

#### Response

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "fullname": "Nguyễn Văn A",
    "role": "USER",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  },
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

#### Errors

| Code | Status | Description |
|------|--------|-------------|
| `INVALID_CREDENTIALS` | 401 | Email hoặc password không đúng |
| `USER_INACTIVE` | 403 | Tài khoản bị vô hiệu hóa |

---

### 3. Refresh Token - Làm mới token

```
POST /api/v1/auth/refresh
```

Làm mới access token bằng refresh token.

#### Request Body

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Errors

| Code | Status | Description |
|------|--------|-------------|
| `INVALID_TOKEN` | 401 | Refresh token không hợp lệ hoặc đã hết hạn |
| `TOKEN_REVOKED` | 401 | Token đã bị thu hồi |

---

### 4. Logout - Đăng xuất

```
POST /api/v1/auth/logout
```

Đăng xuất và thu hồi token.

**Yêu cầu xác thực:** Bearer Token

#### Headers

```
Authorization: Bearer <access_token>
```

#### Request Body

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "all": false
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `refresh_token` | string | Yes | Refresh token cần thu hồi |
| `all` | boolean | No | `true` = thu hồi tất cả token của user |

#### Response

```json
{
  "message": "Logged out successfully"
}
```

---

### 5. Get Current User - Lấy thông tin user

```
GET /api/v1/auth/me
```

Lấy thông tin người dùng đang đăng nhập.

**Yêu cầu xác thực:** Bearer Token

#### Headers

```
Authorization: Bearer <access_token>
```

#### Response

```json
{
  "id": 1,
  "email": "user@example.com",
  "fullname": "Nguyễn Văn A",
  "role": "USER",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Errors

| Code | Status | Description |
|------|--------|-------------|
| `UNAUTHORIZED` | 401 | Chưa đăng nhập hoặc token hết hạn |
| `USER_NOT_FOUND` | 404 | Không tìm thấy user |

---

## Token Information

### Access Token
- **Thời hạn:** 30 phút (1800 giây)
- **Dùng cho:** Xác thực các API request
- **Header:** `Authorization: Bearer <access_token>`

### Refresh Token
- **Thời hạn:** 7 ngày
- **Dùng cho:** Làm mới access token khi hết hạn
- **Lưu trữ:** Secure, HttpOnly cookie hoặc secure storage

---

## Code Examples

### cURL

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Password123","fullname":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Password123"}'

# Get current user
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"

# Refresh token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'

# Logout
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>","all":false}'
```

### JavaScript/TypeScript

```typescript
// Register
const response = await fetch('/api/v1/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'Password123',
    fullname: 'Test User'
  })
});
const { user, tokens } = await response.json();

// Login
const loginResponse = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'Password123'
  })
});

// Authenticated request
const meResponse = await fetch('/api/v1/auth/me', {
  headers: { 'Authorization': `Bearer ${tokens.access_token}` }
});
```

### Python

```python
import httpx

# Login
response = httpx.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "user@example.com", "password": "Password123"}
)
data = response.json()
access_token = data["tokens"]["access_token"]

# Get current user
me_response = httpx.get(
    "http://localhost:8000/api/v1/auth/me",
    headers={"Authorization": f"Bearer {access_token}"}
)
user = me_response.json()
```

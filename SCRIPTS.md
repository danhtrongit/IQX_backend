# Scripts Tự Động cho Backend IQX

Các script shell để quản lý backend IQX một cách dễ dàng.

## 📋 Danh sách Scripts

### 1. `setup.sh` - Thiết lập ban đầu
Script này thiết lập môi trường phát triển lần đầu tiên.

**Chức năng:**
- Tạo virtual environment
- Cài đặt dependencies
- Tạo file .env từ .env.example
- Chạy database migrations
- Tạo admin user mặc định
- Tùy chọn: Đồng bộ danh sách mã chứng khoán

**Cách dùng:**
```bash
cd backend
./setup.sh
```

**Khi nào dùng:** Chạy lần đầu tiên hoặc khi cần reset môi trường hoàn toàn.

---

### 2. `start.sh` - Khởi động server
Script chính để chạy backend server.

**Chức năng:**
- Kiểm tra và tạo virtual environment nếu cần
- Cài đặt dependencies nếu chưa có
- Kiểm tra file .env
- Kiểm tra kết nối MySQL
- Chạy migrations
- Khởi động FastAPI server với Uvicorn

**Cách dùng:**
```bash
# Chạy với cấu hình mặc định (0.0.0.0:8000)
./start.sh

# Chỉ định host và port
./start.sh localhost 8080

# Tắt auto-reload (production mode)
./start.sh 0.0.0.0 8000 --no-reload
```

**Tham số:**
- `$1` - Host (mặc định: 0.0.0.0)
- `$2` - Port (mặc định: 8000)
- `$3` - --no-reload để tắt auto-reload

**Output:**
- ✅ Các bước kiểm tra và chuẩn bị
- 🌐 Link API documentation: http://localhost:8000/docs
- 🧪 Link test page: http://localhost:8000/test-realtime

---

### 3. `stop.sh` - Dừng server
Dừng tất cả tiến trình backend đang chạy.

**Chức năng:**
- Tìm tất cả process uvicorn đang chạy app.main:app
- Kill các process một cách graceful
- Force kill nếu cần thiết

**Cách dùng:**
```bash
./stop.sh
```

---

### 4. `restart.sh` - Khởi động lại server
Dừng và khởi động lại server.

**Chức năng:**
- Gọi stop.sh để dừng server
- Gọi start.sh để khởi động lại

**Cách dùng:**
```bash
./restart.sh
```

---

## 🚀 Quy trình làm việc thông thường

### Lần đầu tiên setup project:
```bash
cd backend

# 1. Thiết lập môi trường
./setup.sh

# 2. Chỉnh sửa .env nếu cần
nano .env

# 3. Chạy server
./start.sh
```

### Ngày làm việc bình thường:
```bash
cd backend

# Chạy server
./start.sh

# Khi muốn dừng
# Ctrl+C hoặc
./stop.sh
```

### Khi có thay đổi code:
```bash
# Server sẽ tự động reload nếu chạy với --reload (mặc định)
# Không cần làm gì cả!

# Nếu cần restart thủ công:
./restart.sh
```

---

## 🔧 Yêu cầu hệ thống

- **Python**: 3.11+
- **MySQL**: 8.0+
- **OS**: macOS/Linux (có thể cần chỉnh sửa cho Windows)

---

## 📝 Lưu ý

1. **Virtual Environment**: Tất cả scripts tự động tạo và sử dụng `venv/`
2. **Dependencies**: Được cache với marker file `venv/.requirements_installed`
3. **MySQL**: Cần đảm bảo MySQL đang chạy và database đã được tạo
4. **.env**: Phải được cấu hình đúng trước khi chạy

---

## ⚙️ Cấu hình .env

Các biến quan trọng cần cấu hình:

```bash
# Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=iqx
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=iqx_db

# JWT
JWT_SECRET=your-secret-key-here-change-in-production

# App
DEBUG=true
APP_NAME=IQX Backend
```

---

## 🐛 Xử lý lỗi

### Lỗi: "MySQL connection failed"
```bash
# Kiểm tra MySQL đang chạy
mysql -u root -p

# Tạo database nếu chưa có
CREATE DATABASE iqx_db;
CREATE USER 'iqx'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON iqx_db.* TO 'iqx'@'localhost';
FLUSH PRIVILEGES;
```

### Lỗi: "Python 3 is not installed"
```bash
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt install python3.11
```

### Lỗi: "Dependencies installation failed"
```bash
# Xóa venv và tạo lại
rm -rf venv
./setup.sh
```

### Server không dừng được
```bash
# Force kill tất cả uvicorn processes
pkill -9 -f uvicorn
```

---

## 🎯 API Endpoints sau khi chạy

| URL | Mô tả |
|-----|-------|
| http://localhost:8000 | Root |
| http://localhost:8000/docs | Swagger UI (API Documentation) |
| http://localhost:8000/redoc | ReDoc (Alternative API Docs) |
| http://localhost:8000/test-realtime | WebSocket Test Page |
| http://localhost:8000/health | Health Check |

---

## 👤 Admin mặc định

```
Email: admin@iqx.local
Password: Admin@12345
```

**⚠️ Quan trọng:** Đổi password sau khi login lần đầu!

---

## 📚 Tài liệu thêm

Xem [README.md](README.md) chính để biết thêm về:
- API endpoints chi tiết
- Trading system
- WebSocket streaming
- Testing
- Deployment

---

## 🤝 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra logs trong terminal
2. Đảm bảo MySQL đang chạy
3. Kiểm tra .env configuration
4. Xem [README.md](README.md) để biết thêm chi tiết

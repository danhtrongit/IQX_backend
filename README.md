# IQX Backend

FastAPI backend với Clean Architecture cho hệ thống IQX.

## Tech Stack

- **Python 3.11+**
- **FastAPI** - Web framework
- **Uvicorn/Gunicorn** - ASGI server
- **SQLAlchemy 2.0** - Async ORM
- **MySQL 8+** - Database
- **Alembic** - Migrations
- **JWT** - Authentication
- **bcrypt** - Password hashing

## Project Structure

```
app/
├── core/           # Config, logging, errors
├── domain/         # Entities, interfaces (pure business)
├── application/    # Use cases, services, DTOs
├── infrastructure/ # DB, repositories, security impl
└── presentation/   # FastAPI routers, middleware
```

## Quick Start

### 1. Local Development

```bash
# Clone và cd vào backend
cd backend

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc: venv\Scripts\activate  # Windows

# Install dependencies
pip install -e ".[dev]"

# Copy env file
cp .env.example .env
# Edit .env với config MySQL local của bạn

# Tạo database trong MySQL local
mysql -u root -p
> CREATE DATABASE iqx_db;
> CREATE USER 'iqx'@'localhost' IDENTIFIED BY 'iqx_password';
> GRANT ALL PRIVILEGES ON iqx_db.* TO 'iqx'@'localhost';
> FLUSH PRIVILEGES;

# Chạy migrations
alembic upgrade head

# Seed admin user
python scripts/seed_admin.py

# Sync symbols from vnstock
python scripts/sync_symbols.py

# Chạy server (dev)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Test realtime page
# Open browser: http://localhost:8000/test-realtime
```

## Test Pages

| URL | Description |
|-----|-------------|
| `/test-realtime` | WebSocket realtime test page (Stock prices & Market indices) |
| `/docs` | Swagger UI API documentation |
| `/redoc` | ReDoc API documentation |

## API Endpoints

Base URL: `http://localhost:8000/api/v1`

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login user |
| POST | `/auth/refresh` | Refresh tokens |
| POST | `/auth/logout` | Logout user |
| GET | `/auth/me` | Get current user |

### Symbols

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/symbols` | List symbols (with filters) |
| GET | `/symbols/search?q=` | Search symbols by name/code |
| GET | `/symbols/industries` | List ICB industries |
| GET | `/symbols/{symbol}` | Get symbol detail |
| POST | `/symbols/sync` | Sync from vnstock (auth required) |

### Market (Index Data)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/market/overview` | All major indices (VNINDEX, HNX, UPCOM, VN30) |
| GET | `/market/indices/{code}` | Single index data |
| GET | `/market/indices/{code}/history` | Index historical data |

### Quotes (Price Data)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/quotes/{symbol}/history` | Historical OHLCV data |
| GET | `/quotes/{symbol}/intraday` | Intraday trades |
| POST | `/quotes/price-board` | Realtime price board (multiple symbols) |
| GET | `/quotes/{symbol}/depth` | Price depth |
| GET | `/quotes/{symbol}/trading-stats` | Trading statistics |

### Financials

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/financials/{symbol}/balance-sheet` | Balance sheet |
| GET | `/financials/{symbol}/income-statement` | Income statement |
| GET | `/financials/{symbol}/cash-flow` | Cash flow statement |
| GET | `/financials/{symbol}/ratio` | Financial ratios (ROE, ROA, P/E, etc.) |

### Company

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/company/{symbol}/overview` | Company profile & info |
| GET | `/company/{symbol}/shareholders` | Major shareholders |
| GET | `/company/{symbol}/officers` | Board members & executives |
| GET | `/company/{symbol}/events` | Corporate events (dividends, splits) |
| GET | `/company/{symbol}/news` | Company news |
| GET | `/company/{symbol}/detail` | Stock detail (price, market cap, ratios, foreign ownership) |

#### Stock Detail Response

```json
GET /api/v1/company/VCB/detail
{
  "symbol": "VCB",
  "match_price": 56900.0,
  "reference_price": 56800.0,
  "ceiling_price": 60700.0,
  "floor_price": 52900.0,
  "price_change": 100.0,
  "percent_price_change": 0.00176,
  "total_volume": 6378752.0,
  "highest_price_1_year": 70092.0,
  "lowest_price_1_year": 51626.0,
  "foreign_total_volume": 4275782.0,
  "foreign_total_room": 2506702528.0,
  "foreign_holding_room": 1774056300.0,
  "current_holding_ratio": 0.212,
  "max_holding_ratio": 0.3,
  "market_cap": 475437912848600.0,
  "issue_share": 8355675094.0,
  "charter_capital": 83556750940000.0,
  "pe": 13.54,
  "pb": 2.14,
  "eps": 1079.57,
  "bvps": 26650.01,
  "roe": 0.168,
  "roa": 0.016,
  "ev": 318019294970000.0,
  "dividend": 0.0
}
```

Fields:
- **Price**: match_price, reference_price, ceiling/floor, price_change
- **52-week**: highest_price_1_year, lowest_price_1_year
- **Foreign**: current_holding_ratio (% sở hữu NN), foreign_total_room
- **Market Cap**: market_cap (Vốn hóa = match_price × issue_share)
- **Shares**: issue_share (SLCP lưu hành), charter_capital
- **Ratios**: PE, PB, EPS, BVPS, ROE, ROA, D/E (Nợ/VCSH)

### Insight (Market Analysis)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/insight/top/foreign-buy` | Top stocks with highest foreign net buy |
| GET | `/insight/top/foreign-sell` | Top stocks with highest foreign net sell |
| GET | `/insight/top/gainer` | Top gaining stocks |
| GET | `/insight/top/loser` | Top losing stocks |
| GET | `/insight/top/value` | Top stocks by trading value |
| GET | `/insight/top/volume` | Top stocks by abnormal volume |
| GET | `/insight/top/deal` | Top stocks by block deal |
| GET | `/insight/{symbol}/proprietary` | Proprietary trading history (tự doanh) |
| GET | `/insight/{symbol}/foreign` | Foreign trading history per symbol |

#### Query Parameters

- `index`: VNINDEX, HNXINDEX, UPCOMINDEX (for top APIs)
- `date`: YYYY-MM-DD (for foreign buy/sell)
- `limit`: Number of results (default 10)
- `start`, `end`: Date range for per-symbol APIs

#### Example Responses

```json
GET /api/v1/insight/top/foreign-buy?limit=3
{
  "type": "buy",
  "date": "2025-12-17",
  "data": [
    {"symbol": "HDB", "date": "2025-12-17", "net_value": 66756020000},
    {"symbol": "MWG", "date": "2025-12-17", "net_value": 58012560000},
    {"symbol": "GEX", "date": "2025-12-17", "net_value": 52336220000}
  ],
  "count": 3
}
```

```json
GET /api/v1/insight/VNM/proprietary?limit=3
{
  "symbol": "VNM",
  "data": [
    {
      "trading_date": "2025-12-16",
      "buy_volume": 575100, "buy_value": 36495900000,
      "sell_volume": 333705, "sell_value": 21248060000,
      "net_volume": 241395, "net_value": 15247840000
    }
  ],
  "count": 3
}
```

### Trading (Requires Auth)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/trading/wallet` | Get wallet (balance, locked, available) |
| GET | `/trading/positions` | Get stock positions |
| POST | `/trading/bootstrap/grant-initial-cash` | Grant 1B VND (idempotent) |
| POST | `/trading/orders` | Place order (MARKET/LIMIT, BUY/SELL) |
| GET | `/trading/orders` | List orders (with filters) |
| GET | `/trading/orders/{id}` | Get order detail |
| POST | `/trading/orders/{id}/cancel` | Cancel order |
| GET | `/trading/trades` | Get trade history |
| GET | `/trading/ledger` | Get ledger (audit trail) |

#### Trading Rules

- **Initial Cash**: 1,000,000,000 VND granted on first activation
- **T0 Settlement**: Orders settle immediately (no T+2)
- **Fee**: 0.1% of trade value
- **Order Types**:
  - MARKET: Execute at current market price
  - LIMIT: Execute when price reaches limit
- **Market Price**: Uses realtime price during trading hours (9:00-11:30, 13:00-15:00), closing price otherwise

#### Place Order Example

```json
POST /api/v1/trading/orders
{
  "symbol": "VNM",
  "side": "BUY",
  "type": "MARKET",
  "quantity": 100
}
```

```json
POST /api/v1/trading/orders
{
  "symbol": "FPT",
  "side": "SELL",
  "type": "LIMIT",
  "quantity": 50,
  "limit_price": 120000,
  "client_order_id": "my-order-001"
}
```

### WebSocket Streaming (Realtime)

| Endpoint | Description |
|----------|-------------|
| `ws://host/api/v1/ws/prices?symbols=VNM,FPT` | Realtime price & index stream |
| GET `/ws/stream/status` | Stream connection status |
| POST `/ws/stream/connect` | Connect to price stream |
| POST `/ws/stream/disconnect` | Disconnect from stream |
| POST `/ws/stream/subscribe` | Subscribe to symbols |
| GET `/ws/stream/prices` | Get cached prices |

#### WebSocket Connection

```javascript
// Connect với symbols ban đầu
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/prices?symbols=VNM,FPT,VCB');

ws.onopen = () => console.log('Connected');
ws.onclose = () => console.log('Disconnected');
ws.onerror = (e) => console.error('Error:', e);
```

#### Receiving Data

```javascript
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  
  switch (msg.type) {
    case 'price':
      // Stock price realtime update
      console.log('Stock:', msg.data);
      /*
      {
        "symbol": "VNM",
        "last_price": 75000,
        "last_volume": 100,
        "change": 500,
        "change_percent": 0.67,
        "total_volume": 1234567,
        "high_price": 76000,
        "low_price": 74500,
        "open_price": 74800,
        "average_price": 75200,
        "side": "BU",  // BU=Buy Up, SD=Sell Down, UN=Unchanged
        "timestamp": 1234567890.123,
        "event_type": "stock"
      }
      */
      break;
      
    case 'index':
      // Market index realtime update (VNINDEX, HNX, UPCOM)
      console.log('Index:', msg.data);
      /*
      {
        "index_id": "VNINDEX",
        "market_code": "HOSE",
        "current_index": 1250.68,
        "open_index": 1240.00,
        "change": 10.68,
        "percent_change": 0.86,
        "volume": 850000000,
        "value": 23450000000000,
        "advances": 200,
        "declines": 150,
        "unchanged": 50,
        "timestamp": 1234567890.123
      }
      */
      break;
      
    case 'subscribed':
      console.log('Subscribed to:', msg.symbols);
      break;
      
    case 'unsubscribed':
      console.log('Unsubscribed from:', msg.symbols);
      break;
      
    case 'cached_prices':
      console.log('Cached prices:', msg.data);
      break;
      
    case 'indices':
      console.log('Cached indices:', msg.data);
      break;
      
    case 'pong':
      console.log('Pong received');
      break;
      
    case 'error':
      console.error('Error:', msg.message);
      break;
  }
};
```

#### Sending Commands

```javascript
// Subscribe to more symbols
ws.send(JSON.stringify({ 
  action: 'subscribe', 
  symbols: ['ACB', 'TCB', 'VCB'] 
}));

// Unsubscribe from symbols
ws.send(JSON.stringify({ 
  action: 'unsubscribe', 
  symbols: ['VNM'] 
}));

// Get cached prices for subscribed symbols
ws.send(JSON.stringify({ action: 'get_cached' }));

// Get cached index data (VNINDEX, HNX, UPCOM)
ws.send(JSON.stringify({ action: 'get_indices' }));

// Ping (keep-alive)
ws.send(JSON.stringify({ action: 'ping' }));
```

#### Stream Management APIs

```bash
# Check stream status
GET /api/v1/ws/stream/status

# Manually connect stream (auto-connects on first WebSocket client)
POST /api/v1/ws/stream/connect?market=HOSE

# Disconnect stream
POST /api/v1/ws/stream/disconnect

# Subscribe symbols to stream
POST /api/v1/ws/stream/subscribe
Body: ["VNM", "FPT", "VCB"]

# Get cached prices
GET /api/v1/ws/stream/prices?symbols=VNM,FPT
```

#### Notes

- Stream **auto-connects** when first WebSocket client connects
- **Index data** (VNINDEX, HNX, UPCOM) is broadcast to ALL connections automatically
- **Stock prices** are only sent to connections subscribed to that symbol
- Use `*` to subscribe to all symbols: `?symbols=*`
- Data is cached - use `get_cached` or `get_indices` to get latest values

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Default Admin

```
Email: admin@iqx.local
Password: Admin@12345
```

## Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_auth.py -v
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | IQX Backend | Application name |
| `DEBUG` | false | Debug mode |
| `MYSQL_HOST` | localhost | MySQL host |
| `MYSQL_PORT` | 3306 | MySQL port |
| `MYSQL_USER` | iqx | MySQL user |
| `MYSQL_PASSWORD` | iqx_password | MySQL password |
| `MYSQL_DATABASE` | iqx_db | MySQL database |
| `JWT_SECRET` | - | JWT secret key (required) |
| `JWT_ACCESS_EXPIRES_MIN` | 30 | Access token expiry (minutes) |
| `JWT_REFRESH_EXPIRES_DAYS` | 7 | Refresh token expiry (days) |

## Code Quality

```bash
# Lint
ruff check .

# Format
ruff format .

# Type check
mypy app
```

## License

MIT

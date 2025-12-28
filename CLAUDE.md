# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IQX Backend is a FastAPI-based trading platform backend with **Clean Architecture** (Domain-Driven Design). It provides Vietnamese stock market data, real-time price streaming, and paper trading capabilities.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), MySQL 8+, Alembic, WebSocket (python-socketio)

## Architecture

The codebase follows **Clean Architecture** with strict separation of concerns:

```
app/
├── core/              # Cross-cutting: config, logging, errors, cache
├── domain/            # Business entities & interfaces (pure logic)
│   ├── user/          # User entities, value objects
│   ├── symbol/        # Symbol entities
│   └── trading/       # Trading entities (Order, Position, Wallet)
├── application/       # Use cases & services (orchestration)
│   ├── user/          # User services (registration, auth)
│   ├── symbol/        # Symbol services
│   ├── trading/       # Trading services (place order, manage wallet)
│   ├── quote/         # Price data services
│   ├── financial/     # Financial statement services
│   ├── market/        # Market index services
│   ├── insight/       # Market analysis services
│   ├── chat/          # AI chat (Mr. Arix) services
│   └── [service]/dtos.py  # Request/Response DTOs for each service
├── infrastructure/    # External dependencies & implementations
│   ├── db/            # Database session management
│   ├── models/        # SQLAlchemy models (DB schema)
│   ├── repositories/  # Repository implementations
│   ├── security/      # JWT, password hashing
│   ├── vnstock/       # Vietnam stock data provider adapter
│   ├── vietcap/       # Alternative data provider
│   ├── streaming/     # WebSocket price stream manager
│   └── trading/       # Trading engine implementation
└── presentation/      # HTTP/WebSocket layer
    ├── api/v1/        # API routes
    │   └── endpoints/ # Route handlers by domain
    ├── deps/          # FastAPI dependencies (auth, DB session)
    └── middleware/    # Request ID, rate limiting
```

### Dependency Flow Rules

**CRITICAL:** Follow these rules strictly when modifying code:

1. **Domain layer** (`domain/`) - Pure business logic
   - NO imports from `infrastructure/`, `application/`, or `presentation/`
   - Only depends on standard library and domain models
   - Defines interfaces (abstract base classes) for repositories

2. **Application layer** (`application/`) - Use cases
   - Imports from `domain/` only
   - NO imports from `infrastructure/` or `presentation/`
   - Services orchestrate domain logic using repository interfaces

3. **Infrastructure layer** (`infrastructure/`) - External systems
   - Imports from `domain/` to implement interfaces
   - Contains concrete implementations (repositories, external APIs)

4. **Presentation layer** (`presentation/`) - HTTP handlers
   - Imports from `application/` (services) and `domain/` (DTOs)
   - Dependency injection happens here (FastAPI `Depends()`)

**Example pattern:**
- `domain/user/interfaces.py` defines `UserRepository` interface
- `infrastructure/repositories/user_repo.py` implements `SQLAlchemyUserRepository`
- `application/user/services.py` uses `UserRepository` interface (injected)
- `presentation/api/v1/endpoints/auth.py` calls application services

## Development Commands

### Setup & Run

```bash
# First-time setup (creates venv, installs deps, runs migrations, seeds admin)
./setup.sh

# Start development server (auto-reload enabled)
./start.sh

# Start on specific host/port
./start.sh localhost 8080

# Production mode (no auto-reload)
./start.sh 0.0.0.0 8000 --no-reload

# Stop server
./stop.sh

# Restart server
./restart.sh
```

### Using Virtual Environment

```bash
# Run any command in venv
./run-in-venv.sh <command>

# Examples
./run-in-venv.sh alembic upgrade head
./run-in-venv.sh python scripts/seed_admin.py
./run-in-venv.sh pytest tests/test_auth.py -v

# Manual activation (for multiple commands)
source venv/bin/activate
# ... do work ...
deactivate
```

### Database Migrations

```bash
# Create new migration (auto-generate from model changes)
./run-in-venv.sh alembic revision --autogenerate -m "description"

# Apply migrations
./run-in-venv.sh alembic upgrade head

# Rollback one migration
./run-in-venv.sh alembic downgrade -1

# View migration history
./run-in-venv.sh alembic history
```

### Testing

```bash
# Run all tests
./run-in-venv.sh pytest

# Run with coverage
./run-in-venv.sh pytest --cov=app --cov-report=html

# Run specific test file
./run-in-venv.sh pytest tests/test_auth.py -v

# Run specific test function
./run-in-venv.sh pytest tests/test_auth.py::test_register -v

# Run tests matching pattern
./run-in-venv.sh pytest -k "test_login" -v
```

### Code Quality

```bash
# Lint (check for issues)
./run-in-venv.sh ruff check .

# Format code
./run-in-venv.sh ruff format .

# Type check
./run-in-venv.sh mypy app

# Run all checks before commit
./run-in-venv.sh ruff check . && ruff format . && mypy app
```

### Utility Scripts

```bash
# Seed admin user (email: admin@iqx.local, password: Admin@12345)
./run-in-venv.sh python scripts/seed_admin.py

# Sync stock symbols from vnstock (takes time)
./run-in-venv.sh python scripts/sync_symbols.py

# Test foreign trading data
./run-in-venv.sh python scripts/test_foreign_trade.py
```

## Key Configuration

### Environment Variables (.env)

Critical settings in `.env`:
- `MYSQL_*` - Database connection
- `JWT_SECRET` - Must change in production
- `ENABLE_PRICE_STREAM` - Auto-start WebSocket stream (default: False)
- `AI_API_KEY` - For Mr. Arix chat feature
- `DEBUG` - Enable debug mode (default: False)

### WebSocket Price Streaming

The app includes a real-time price streaming system:
- **Auto-start:** Set `ENABLE_PRICE_STREAM=true` in `.env`
- **Manager:** `app/infrastructure/streaming/price_stream.py`
- **Endpoints:** `/api/v1/ws/prices` (WebSocket), `/api/v1/ws/stream/*` (HTTP controls)
- **Test page:** http://localhost:8000/test-realtime

Stream connects to external market data provider and broadcasts:
- Stock prices (to subscribed clients only)
- Index data (VNINDEX, HNX, UPCOM - broadcast to all clients)

### Trading System

Paper trading with T0 settlement (immediate execution):
- Bootstrap: POST `/api/v1/trading/bootstrap/grant-initial-cash` grants 1B VND
- Orders: Market & Limit types, 0.1% fee
- Market hours: 9:00-11:30, 13:00-15:00 (uses real-time prices), outside uses closing price

## API Documentation

**Swagger UI:** http://localhost:8000/docs
**ReDoc:** http://localhost:8000/redoc

### Main API Groups

- `/api/v1/auth` - Registration, login, refresh tokens
- `/api/v1/symbols` - Stock symbols, search, industries
- `/api/v1/quotes` - Historical OHLCV, intraday, price board
- `/api/v1/financials` - Balance sheet, income statement, cash flow, ratios
- `/api/v1/company` - Company profile, shareholders, events, news
- `/api/v1/market` - Index data (VNINDEX, HNX, UPCOM)
- `/api/v1/insight` - Top movers, foreign/proprietary trading
- `/api/v1/trading` - Wallet, positions, orders, trades (auth required)
- `/api/v1/ws/prices` - WebSocket real-time prices
- `/api/v1/chat` - AI assistant (Mr. Arix)

## Common Patterns

### Adding a New Feature

1. **Define domain entities** in `domain/[feature]/entities.py` if needed
2. **Define repository interface** in `domain/[feature]/interfaces.py`
3. **Create DTOs** in `application/[feature]/dtos.py` (Pydantic models)
4. **Implement service** in `application/[feature]/services.py`
5. **Create repository** in `infrastructure/repositories/[feature]_repo.py`
6. **Add database model** in `infrastructure/models/[feature]_model.py`
7. **Create migration** with `alembic revision --autogenerate`
8. **Add API endpoint** in `presentation/api/v1/endpoints/[feature].py`
9. **Register router** in `presentation/api/v1/router.py`
10. **Write tests** in `tests/test_[feature].py`

### Adding a New Endpoint

```python
# presentation/api/v1/endpoints/example.py
from fastapi import APIRouter, Depends
from app.presentation.deps import get_current_user
from app.application.example.services import ExampleService
from app.application.example.dtos import ExampleRequest, ExampleResponse

router = APIRouter(prefix="/example", tags=["Example"])

@router.post("/action", response_model=ExampleResponse)
async def do_action(
    request: ExampleRequest,
    service: ExampleService = Depends(),
    user = Depends(get_current_user),  # For authenticated endpoints
):
    return await service.do_action(request, user.id)
```

### Database Model + Migration

```python
# 1. Add model in infrastructure/models/
from app.infrastructure.models.base import Base
from sqlalchemy import Column, Integer, String

class NewModel(Base):
    __tablename__ = "new_table"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

# 2. Import in infrastructure/models/__init__.py
from .new_model import NewModel

# 3. Generate migration
./run-in-venv.sh alembic revision --autogenerate -m "add new_table"

# 4. Review and edit migration file in alembic/versions/
# 5. Apply migration
./run-in-venv.sh alembic upgrade head
```

## Troubleshooting

### "hatchling.build" error when installing dependencies
Fixed in pyproject.toml with `[tool.hatch.build.targets.wheel] packages = ["app"]`

### Database connection issues
1. Ensure MySQL is running
2. Check `.env` credentials
3. Verify database exists: `mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS iqx_db;"`

### WebSocket not connecting
1. Check `ENABLE_PRICE_STREAM` in `.env`
2. View stream status: `curl http://localhost:8000/api/v1/ws/stream/status`
3. Check logs for connection errors

### Tests failing with DB errors
Tests use SQLite in-memory DB, not MySQL. Check `tests/conftest.py` for test DB setup.

## Important Notes

- **Never commit** `.env` file (contains secrets)
- **Always run migrations** after pulling model changes
- **Follow Clean Architecture** - respect layer boundaries
- **Use DTOs** - never expose domain entities or DB models directly in API responses
- **Dependency injection** - services receive repositories via constructor, endpoints use `Depends()`
- **Async everywhere** - all DB operations and external API calls must be async
- **Error handling** - use `AppError` from `app/core/errors` for business logic errors

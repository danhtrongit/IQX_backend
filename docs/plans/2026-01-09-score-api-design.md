# Score API Design

## Overview

Two APIs for stock score ranking and history based on OHLC data.

**Formula:**
```
SCORE = P × √V

P = ((Close - MA) / MA) × 100   # Price deviation percentage
V = Volume / Vol_Avg             # Volume ratio
```

## Database Changes

### Add MA columns to `stock_ohlc_daily`

```sql
ALTER TABLE stock_ohlc_daily ADD COLUMN (
    ma5 DECIMAL(12,2) NULL,
    ma10 DECIMAL(12,2) NULL,
    ma20 DECIMAL(12,2) NULL,
    ma30 DECIMAL(12,2) NULL,
    ma50 DECIMAL(12,2) NULL,
    ma100 DECIMAL(12,2) NULL,
    ma200 DECIMAL(12,2) NULL,
    vol_ma5 BIGINT NULL,
    vol_ma10 BIGINT NULL,
    vol_ma20 BIGINT NULL,
    vol_ma30 BIGINT NULL,
    vol_ma50 BIGINT NULL,
    vol_ma100 BIGINT NULL,
    vol_ma200 BIGINT NULL
);

CREATE INDEX idx_ohlc_date ON stock_ohlc_daily(trade_date);
```

## API Endpoints

### 1. GET `/api/v1/score/ranking`

**Query params:**
- `ma_period`: enum [5, 10, 20, 30, 50, 100, 200] - required
- `exchange`: string, comma-separated (e.g., "HOSE,HNX") - optional
- `limit`: int, default 50, max 500
- `offset`: int, default 0
- `sort`: enum ["desc", "asc"] - default "desc"

**Response:**
```json
{
  "items": [
    {
      "rank": 1,
      "symbol": "VNM",
      "exchange": "HOSE",
      "score": 12.5,
      "p": 8.2,
      "v": 2.3,
      "close": 75000,
      "ma": 69300,
      "volume": 5200000,
      "vol_avg": 2260000
    }
  ],
  "total": 1695,
  "ma_period": 20,
  "trade_date": "2026-01-09"
}
```

### 2. GET `/api/v1/score/history/{symbol}`

**Query params:**
- `ma_period`: enum [5, 10, 20, 30, 50, 100] - required
- `range`: enum ["week", "month", "year"] - required

**Response:**
```json
{
  "symbol": "VNM",
  "ma_period": 20,
  "data": [
    {
      "date": "2026-01-09",
      "score": 12.5,
      "p": 8.2,
      "v": 2.3,
      "close": 75000,
      "ma": 69300,
      "volume": 5200000,
      "vol_avg": 2260000
    }
  ]
}
```

## Calculation Logic

**Score Formula:**
```python
P = ((close - ma) / ma) * 100  # e.g., 5% → 5
V = volume / vol_avg           # Volume ratio
SCORE = P * sqrt(V)            # Final score
```

**Edge cases:**
- MA = NULL → Exclude from ranking
- Volume = 0 → Score = 0
- MA = 0 → Exclude (safety check)

## MA Calculation Job

- Runs after each OHLC sync
- Manual command: `python -m scripts.ohlc_sync calculate-ma`
- Only updates records with NULL MA or new sync date

## File Structure

```
backend/
├── alembic/versions/
│   └── 006_add_ma_columns_to_ohlc.py
├── app/
│   ├── application/score/
│   │   ├── __init__.py
│   │   ├── dtos.py
│   │   └── services.py
│   ├── infrastructure/repositories/
│   │   └── score_repo.py
│   └── presentation/api/v1/endpoints/
│       └── score.py
└── scripts/
    └── ohlc_sync.py  # Add calculate-ma command
```

## Implementation Order

1. Migration: Add MA columns
2. Add calculate_ma() to sync service
3. Run calculate_ma for existing data
4. Create DTOs
5. Create repository
6. Create service
7. Create endpoints & register router
8. Test APIs

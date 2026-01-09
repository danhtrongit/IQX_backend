"""Score DTOs (Data Transfer Objects)."""
from datetime import date
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field


class MAPeriod(int, Enum):
    """Moving Average periods."""
    MA5 = 5
    MA10 = 10
    MA20 = 20
    MA30 = 30
    MA50 = 50
    MA100 = 100
    MA200 = 200


class MAPeriodHistory(int, Enum):
    """Moving Average periods for history (excludes MA200)."""
    MA5 = 5
    MA10 = 10
    MA20 = 20
    MA30 = 30
    MA50 = 50
    MA100 = 100


class TimeRange(str, Enum):
    """Time range for score history."""
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class SortOrder(str, Enum):
    """Sort order for ranking."""
    DESC = "desc"
    ASC = "asc"


# =============================================================================
# RANKING API DTOs
# =============================================================================


class ScoreRankingRequest(BaseModel):
    """Request for score ranking API."""
    ma_period: MAPeriod
    exchange: str | None = Field(
        None,
        description="Comma-separated exchange codes (e.g., 'HOSE,HNX')"
    )
    limit: int = Field(50, ge=1, le=500)
    offset: int = Field(0, ge=0)
    sort: SortOrder = SortOrder.DESC


class ScoreRankingItem(BaseModel):
    """Single item in score ranking response."""
    rank: int
    symbol: str
    exchange: str
    score: float
    p: float = Field(description="Price deviation percentage: (close-ma)/ma * 100")
    v: float = Field(description="Volume ratio: volume/vol_avg")
    close: Decimal
    ma: Decimal
    volume: int
    vol_avg: int


class ScoreRankingResponse(BaseModel):
    """Response for score ranking API."""
    items: list[ScoreRankingItem]
    total: int
    ma_period: int
    trade_date: date


# =============================================================================
# HISTORY API DTOs
# =============================================================================


class ScoreHistoryRequest(BaseModel):
    """Request for score history API."""
    ma_period: MAPeriodHistory
    range: TimeRange


class ScoreHistoryItem(BaseModel):
    """Single item in score history response."""
    date: date
    score: float
    p: float
    v: float
    close: Decimal
    ma: Decimal
    volume: int
    vol_avg: int


class ScoreHistoryResponse(BaseModel):
    """Response for score history API."""
    symbol: str
    ma_period: int
    data: list[ScoreHistoryItem]

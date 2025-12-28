
"""Market DTOs."""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class IndexResponse(BaseModel):
    """Market index response."""
    
    index_code: str  # VNINDEX, HNXINDEX, UPCOMINDEX
    index_value: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    ref_value: Optional[float] = None  # Tham chiếu
    open_value: Optional[float] = None  # Mở cửa
    high_value: Optional[float] = None  # Cao nhất
    low_value: Optional[float] = None  # Thấp nhất
    total_volume: Optional[int] = None  # Khối lượng
    total_value: Optional[float] = None  # Giá trị (tỷ)
    advances: Optional[int] = None  # Tăng
    declines: Optional[int] = None  # Giảm
    unchanged: Optional[int] = None  # Đứng giá
    foreign_buy_volume: Optional[int] = None
    foreign_sell_volume: Optional[int] = None
    foreign_net_volume: Optional[int] = None
    timestamp: Optional[datetime] = None


class MarketOverviewResponse(BaseModel):
    """Market overview response."""
    
    indices: List[IndexResponse]
    timestamp: datetime


class IndexHistoryRequest(BaseModel):
    """Index history request."""
    
    start: str = Field(..., description="Start date (YYYY-MM-DD)")
    end: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    interval: str = Field("1D", description="Interval: 1D, 1W, 1M")


class IndexHistoryItem(BaseModel):
    """Index history item."""
    
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class IndexHistoryResponse(BaseModel):
    """Index history response."""
    
    index_code: str
    data: List[IndexHistoryItem]
    count: int

# Market Evaluation
class MarketEvaluationItem(BaseModel):
    date: Optional[str]
    pe: Optional[float]
    pb: Optional[float]
    ps: Optional[float] = None
    dy: Optional[float] = None
    vn_type: Optional[str] = None

class MarketEvaluationResponse(BaseModel):
    data: List[MarketEvaluationItem]
    count: int

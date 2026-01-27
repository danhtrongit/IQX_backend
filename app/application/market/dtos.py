
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


# Allocated Value (Capital Flow / Market Breadth)
class AllocatedValueItem(BaseModel):
    """Single market allocated value data."""
    
    # Raw data from API
    total_increase: Optional[List[Dict[str, Any]]] = Field(None, alias="totalIncrease")
    total_nochange: Optional[List[Dict[str, Any]]] = Field(None, alias="totalNochange")
    total_decrease: Optional[List[Dict[str, Any]]] = Field(None, alias="totalDecrease")
    total_symbol_increase: Optional[List[Dict[str, Any]]] = Field(None, alias="totalSymbolIncrease")
    total_symbol_nochange: Optional[List[Dict[str, Any]]] = Field(None, alias="totalSymbolNochange")
    total_symbol_decrease: Optional[List[Dict[str, Any]]] = Field(None, alias="totalSymbolDecrease")
    
    class Config:
        populate_by_name = True


class AllocatedValueResponse(BaseModel):
    """
    Allocated value response - market breadth data.
    
    When group=HOSE/HNX/UPCOME: data contains 1 item
    When group=ALL: data contains 3 items (HOSE, HNX, UPCOM)
    """
    
    data: List[AllocatedValueItem] = []
    group: str
    time_frame: str = Field(alias="timeFrame")
    count: int = 0
    
    class Config:
        populate_by_name = True


# Allocated ICB (Industry Classification Benchmark)
class AllocatedICBItem(BaseModel):
    """ICB sector allocation item."""
    
    icb_code: Optional[int] = Field(None, alias="icb_code")
    sector_name_vi: Optional[str] = None  # Vietnamese sector name
    sector_name_en: Optional[str] = None  # English sector name
    icb_level: Optional[int] = None  # ICB level (1-4)
    icb_change_percent: Optional[float] = Field(None, alias="icbChangePercent")
    total_price_change: Optional[float] = Field(None, alias="totalPriceChange")
    total_market_cap: Optional[float] = Field(None, alias="totalMarketCap")
    total_value: Optional[float] = Field(None, alias="totalValue")
    total_stock_increase: Optional[int] = Field(None, alias="totalStockIncrease")
    total_stock_decrease: Optional[int] = Field(None, alias="totalStockDecrease")
    total_stock_no_change: Optional[int] = Field(None, alias="totalStockNoChange")
    icb_code_parent: Optional[int] = Field(None, alias="icbCodeParent")
    
    class Config:
        populate_by_name = True



class AllocatedICBResponse(BaseModel):
    """Allocated ICB response - sector allocation by industry."""
    
    data: List[AllocatedICBItem] = []
    group: str
    time_frame: str = Field(alias="timeFrame")
    count: int = 0
    
    class Config:
        populate_by_name = True


# Allocated ICB Detail (Stocks within a sector)
class AllocatedICBStockItem(BaseModel):
    """Stock item within an ICB sector."""
    
    symbol: str
    ref_price: Optional[float] = Field(None, alias="refPrice")
    match_price: Optional[float] = Field(None, alias="matchPrice")
    ceiling_price: Optional[float] = Field(None, alias="ceilingPrice")
    floor_price: Optional[float] = Field(None, alias="floorPrice")
    accumulated_volume: Optional[float] = Field(None, alias="accumulatedVolume")
    accumulated_value: Optional[float] = Field(None, alias="accumulatedValue")
    price_change: Optional[float] = Field(None, alias="priceChange")
    price_change_percent: Optional[float] = Field(None, alias="priceChangePercent")
    market_cap: Optional[float] = Field(None, alias="marketCap")
    
    class Config:
        populate_by_name = True


class AllocatedICBDetailResponse(BaseModel):
    """Allocated ICB detail response - stocks within a sector."""
    
    # Sector summary
    icb_code: int = Field(alias="icb_code")
    sector_name_vi: Optional[str] = None
    sector_name_en: Optional[str] = None
    icb_level: Optional[int] = None
    icb_change_percent: Optional[float] = Field(None, alias="icbChangePercent")
    total_price_change: Optional[float] = Field(None, alias="totalPriceChange")
    total_market_cap: Optional[float] = Field(None, alias="totalMarketCap")
    total_value: Optional[float] = Field(None, alias="totalValue")
    total_stock_increase: Optional[int] = Field(None, alias="totalStockIncrease")
    total_stock_decrease: Optional[int] = Field(None, alias="totalStockDecrease")
    total_stock_no_change: Optional[int] = Field(None, alias="totalStockNoChange")
    icb_code_parent: Optional[int] = Field(None, alias="icbCodeParent")
    
    # Stocks list
    stocks: List[AllocatedICBStockItem] = []
    
    # Request params
    group: str
    time_frame: str = Field(alias="timeFrame")
    
    class Config:
        populate_by_name = True


# Index Impact (Market Leading Stocks)
class IndexImpactStockItem(BaseModel):
    """Stock item in market impact list."""
    
    symbol: str
    impact: Optional[float] = None  # Impact on index (points)
    exchange: Optional[str] = None  # HOSE, HNX, etc.
    organ_name: Optional[str] = Field(None, alias="organName")  # Vietnamese company name
    organ_short_name: Optional[str] = Field(None, alias="organShortName")
    en_organ_name: Optional[str] = Field(None, alias="enOrganName")  # English company name
    en_organ_short_name: Optional[str] = Field(None, alias="enOrganShortName")
    match_price: Optional[float] = Field(None, alias="matchPrice")
    ref_price: Optional[float] = Field(None, alias="refPrice")
    ceiling: Optional[float] = None
    floor: Optional[float] = None
    
    class Config:
        populate_by_name = True


class IndexImpactResponse(BaseModel):
    """Index impact response - market leading stocks."""
    
    top_up: List[IndexImpactStockItem] = Field(default=[], alias="topUp")  # Stocks pulling market up
    top_down: List[IndexImpactStockItem] = Field(default=[], alias="topDown")  # Stocks pulling market down
    group: str
    time_frame: str = Field(alias="timeFrame")
    
    class Config:
        populate_by_name = True


# Top Proprietary Trading
class ProprietaryStockItem(BaseModel):
    """Stock item in proprietary trading list."""
    
    ticker: str
    total_value: Optional[float] = Field(None, alias="totalValue")  # Net value (negative = sell)
    total_volume: Optional[float] = Field(None, alias="totalVolume")
    exchange: Optional[str] = None
    organ_name: Optional[str] = Field(None, alias="organName")
    organ_short_name: Optional[str] = Field(None, alias="organShortName")
    en_organ_name: Optional[str] = Field(None, alias="enOrganName")
    en_organ_short_name: Optional[str] = Field(None, alias="enOrganShortName")
    match_price: Optional[float] = Field(None, alias="matchPrice")
    ref_price: Optional[float] = Field(None, alias="refPrice")
    
    class Config:
        populate_by_name = True


class TopProprietaryResponse(BaseModel):
    """Top proprietary trading response."""
    
    trading_date: Optional[str] = Field(None, alias="tradingDate")
    buy: List[ProprietaryStockItem] = []  # Proprietary buying
    sell: List[ProprietaryStockItem] = []  # Proprietary selling
    exchange: str
    time_frame: str = Field(alias="timeFrame")
    
    class Config:
        populate_by_name = True


# Foreign Net Value
class ForeignNetStockItem(BaseModel):
    """Stock item in foreign trading list."""
    
    symbol: str
    net: Optional[float] = None  # Net buy/sell value
    foreign_buy_value: Optional[float] = Field(None, alias="foreignBuyValue")
    foreign_sell_value: Optional[float] = Field(None, alias="foreignSellValue")
    exchange: Optional[str] = None
    organ_name: Optional[str] = Field(None, alias="organName")
    organ_short_name: Optional[str] = Field(None, alias="organShortName")
    en_organ_name: Optional[str] = Field(None, alias="enOrganName")
    en_organ_short_name: Optional[str] = Field(None, alias="enOrganShortName")
    match_price: Optional[float] = Field(None, alias="matchPrice")
    ref_price: Optional[float] = Field(None, alias="refPrice")
    
    class Config:
        populate_by_name = True


class ForeignNetValueResponse(BaseModel):
    """Foreign net value response."""
    
    net_buy: List[ForeignNetStockItem] = Field(default=[], alias="netBuy")  # Top foreign net buy
    net_sell: List[ForeignNetStockItem] = Field(default=[], alias="netSell")  # Top foreign net sell
    group: str
    time_frame: str = Field(alias="timeFrame")
    
    class Config:
        populate_by_name = True


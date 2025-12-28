
from typing import List, Optional, Any, Dict
from pydantic import BaseModel

class StockListingItem(BaseModel):
    symbol: str
    organ_name: str
    organ_short_name: Optional[str] = None
    exchange: str
    com_group_code: Optional[str] = None
    icb_code: Optional[str] = None
    sector_type: Optional[str] = None
    industry_level_1: Optional[str] = None
    industry_level_2: Optional[str] = None
    industry_level_3: Optional[str] = None
    industry_level_4: Optional[str] = None

class ListingResponse(BaseModel):
    count: int
    data: List[Dict[str, Any]]

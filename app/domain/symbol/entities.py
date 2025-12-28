"""Symbol domain entities."""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class Symbol:
    """Stock symbol entity."""
    
    id: int
    symbol: str
    organ_name: Optional[str] = None
    en_organ_name: Optional[str] = None
    organ_short_name: Optional[str] = None
    exchange: Optional[str] = None  # HOSE, HNX, UPCOM
    type: Optional[str] = None  # STOCK, ETF, CW, BOND
    
    # ICB Industry Classification
    icb_code1: Optional[str] = None
    icb_code2: Optional[str] = None
    icb_code3: Optional[str] = None
    icb_code4: Optional[str] = None
    icb_name2: Optional[str] = None
    icb_name3: Optional[str] = None
    icb_name4: Optional[str] = None
    
    # Company details
    company_profile: Optional[str] = None
    history: Optional[str] = None
    issue_share: Optional[Decimal] = None
    charter_capital: Optional[Decimal] = None
    
    # Metadata
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Industry:
    """ICB Industry entity."""
    
    id: int
    icb_code: str
    icb_name: str
    en_icb_name: Optional[str] = None
    level: int = 1  # 1-4
    parent_code: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

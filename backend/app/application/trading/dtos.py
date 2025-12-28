"""Trading DTOs."""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field


# === Request DTOs ===

class PlaceOrderRequest(BaseModel):
    """Place order request."""
    
    symbol: str = Field(..., min_length=1, max_length=20)
    side: str = Field(..., pattern="^(BUY|SELL)$")
    type: str = Field(..., pattern="^(MARKET|LIMIT)$")
    quantity: Decimal = Field(..., gt=0)
    limit_price: Optional[Decimal] = Field(None, gt=0)
    client_order_id: Optional[str] = Field(None, max_length=50)


class OrderListRequest(BaseModel):
    """Order list request."""
    
    status: Optional[str] = None
    symbol: Optional[str] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class TradeListRequest(BaseModel):
    """Trade list request."""
    
    symbol: Optional[str] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class LedgerListRequest(BaseModel):
    """Ledger list request."""
    
    entry_type: Optional[str] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


# === Response DTOs ===

class WalletResponse(BaseModel):
    """Wallet response."""
    
    balance: Decimal
    locked: Decimal
    available: Decimal
    currency: str
    first_grant_at: Optional[datetime] = None


class PositionResponse(BaseModel):
    """Position response."""
    
    symbol: str
    quantity: Decimal
    locked_quantity: Decimal
    available_quantity: Decimal
    avg_price: Decimal
    market_price: Optional[Decimal] = None
    market_value: Optional[Decimal] = None
    unrealized_pnl: Optional[Decimal] = None


class PositionListResponse(BaseModel):
    """Position list response."""
    
    data: List[PositionResponse]
    total_market_value: Optional[Decimal] = None


class TradeResponse(BaseModel):
    """Trade response."""
    
    id: int
    order_id: int
    symbol: str
    side: str
    quantity: Decimal
    price: Decimal
    fee: Decimal
    value: Decimal
    executed_at: datetime


class OrderResponse(BaseModel):
    """Order response."""
    
    id: int
    symbol: str
    side: str
    type: str
    quantity: Decimal
    limit_price: Optional[Decimal] = None
    status: str
    filled_quantity: Decimal
    remaining_quantity: Decimal
    avg_filled_price: Decimal
    fee_total: Decimal
    price_snapshot: Optional[Decimal] = None
    client_order_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    trades: Optional[List[TradeResponse]] = None


class OrderListResponse(BaseModel):
    """Order list response."""
    
    data: List[OrderResponse]
    count: int


class PlaceOrderResponse(BaseModel):
    """Place order response."""
    
    order: OrderResponse
    wallet: WalletResponse


class CancelOrderResponse(BaseModel):
    """Cancel order response."""
    
    order: OrderResponse
    wallet: WalletResponse


class TradeListResponse(BaseModel):
    """Trade list response."""
    
    data: List[TradeResponse]
    count: int


class LedgerEntryResponse(BaseModel):
    """Ledger entry response."""
    
    id: int
    entry_type: str
    amount: Decimal
    balance_after: Decimal
    ref_type: Optional[str] = None
    ref_id: Optional[int] = None
    meta: Optional[dict] = None
    created_at: datetime


class LedgerListResponse(BaseModel):
    """Ledger list response."""
    
    data: List[LedgerEntryResponse]
    count: int


class GrantCashResponse(BaseModel):
    """Grant initial cash response."""
    
    wallet: WalletResponse
    granted: bool
    message: str

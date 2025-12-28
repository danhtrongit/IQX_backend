"""Trading domain entities."""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class OrderStatus(str, Enum):
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class LedgerEntryType(str, Enum):
    GRANT = "GRANT"
    BUY = "BUY"
    SELL = "SELL"
    FEE = "FEE"
    LOCK = "LOCK"
    UNLOCK = "UNLOCK"
    CANCEL_RELEASE = "CANCEL_RELEASE"


@dataclass
class Wallet:
    """User wallet entity."""
    
    id: int
    user_id: int
    balance: Decimal = Decimal("0")
    locked: Decimal = Decimal("0")
    currency: str = "VND"
    first_grant_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def available(self) -> Decimal:
        """Available balance for trading."""
        return self.balance - self.locked
    
    def can_lock(self, amount: Decimal) -> bool:
        """Check if amount can be locked."""
        return self.available >= amount
    
    def lock(self, amount: Decimal) -> None:
        """Lock amount for order."""
        if not self.can_lock(amount):
            raise ValueError("Insufficient available balance")
        self.locked += amount
    
    def unlock(self, amount: Decimal) -> None:
        """Unlock amount."""
        self.locked = max(Decimal("0"), self.locked - amount)
    
    def deduct(self, amount: Decimal) -> None:
        """Deduct from balance (after trade execution)."""
        self.balance -= amount
    
    def credit(self, amount: Decimal) -> None:
        """Credit to balance."""
        self.balance += amount


@dataclass
class Position:
    """User position (stock holding) entity."""
    
    id: int
    user_id: int
    symbol: str
    quantity: Decimal = Decimal("0")
    locked_quantity: Decimal = Decimal("0")
    avg_price: Decimal = Decimal("0")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def available_quantity(self) -> Decimal:
        """Available quantity for selling."""
        return self.quantity - self.locked_quantity
    
    def can_lock(self, qty: Decimal) -> bool:
        """Check if quantity can be locked."""
        return self.available_quantity >= qty
    
    def lock(self, qty: Decimal) -> None:
        """Lock quantity for sell order."""
        if not self.can_lock(qty):
            raise ValueError("Insufficient available position")
        self.locked_quantity += qty
    
    def unlock(self, qty: Decimal) -> None:
        """Unlock quantity."""
        self.locked_quantity = max(Decimal("0"), self.locked_quantity - qty)
    
    def add(self, qty: Decimal, price: Decimal) -> None:
        """Add to position (after buy)."""
        if self.quantity == Decimal("0"):
            self.avg_price = price
            self.quantity = qty
        else:
            total_value = self.quantity * self.avg_price + qty * price
            self.quantity += qty
            self.avg_price = total_value / self.quantity
    
    def remove(self, qty: Decimal) -> None:
        """Remove from position (after sell)."""
        self.quantity -= qty
        if self.quantity <= Decimal("0"):
            self.quantity = Decimal("0")
            self.avg_price = Decimal("0")


@dataclass
class Order:
    """Trading order entity."""
    
    id: int
    user_id: int
    symbol: str
    side: OrderSide
    type: OrderType
    quantity: Decimal
    limit_price: Optional[Decimal] = None
    status: OrderStatus = OrderStatus.NEW
    filled_quantity: Decimal = Decimal("0")
    avg_filled_price: Decimal = Decimal("0")
    fee_total: Decimal = Decimal("0")
    price_snapshot: Optional[Decimal] = None
    client_order_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    
    @property
    def remaining_quantity(self) -> Decimal:
        """Remaining quantity to fill."""
        return self.quantity - self.filled_quantity
    
    @property
    def is_active(self) -> bool:
        """Check if order is still active."""
        return self.status in (OrderStatus.NEW, OrderStatus.PARTIALLY_FILLED)
    
    def can_cancel(self) -> bool:
        """Check if order can be canceled."""
        return self.status in (OrderStatus.NEW, OrderStatus.PARTIALLY_FILLED)
    
    def fill(self, qty: Decimal, price: Decimal, fee: Decimal) -> None:
        """Fill order (partial or full)."""
        if qty > self.remaining_quantity:
            raise ValueError("Fill quantity exceeds remaining")
        
        # Update avg filled price
        total_value = self.filled_quantity * self.avg_filled_price + qty * price
        self.filled_quantity += qty
        self.avg_filled_price = total_value / self.filled_quantity
        self.fee_total += fee
        
        # Update status
        if self.filled_quantity >= self.quantity:
            self.status = OrderStatus.FILLED
        else:
            self.status = OrderStatus.PARTIALLY_FILLED
    
    def cancel(self) -> None:
        """Cancel order."""
        if not self.can_cancel():
            raise ValueError("Order cannot be canceled")
        self.status = OrderStatus.CANCELED
        self.canceled_at = datetime.utcnow()


@dataclass
class Trade:
    """Trade (fill) entity."""
    
    id: int
    order_id: int
    user_id: int
    symbol: str
    side: OrderSide
    quantity: Decimal
    price: Decimal
    fee: Decimal = Decimal("0")
    executed_at: Optional[datetime] = None


@dataclass
class LedgerEntry:
    """Ledger entry for audit trail."""
    
    id: int
    user_id: int
    entry_type: LedgerEntryType
    amount: Decimal
    balance_after: Decimal
    ref_type: Optional[str] = None
    ref_id: Optional[int] = None
    meta_json: Optional[dict] = None
    created_at: Optional[datetime] = None

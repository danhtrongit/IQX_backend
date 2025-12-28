"""Trading domain repository interfaces."""
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional, List

from app.domain.trading.entities import (
    Wallet,
    Position,
    Order,
    Trade,
    LedgerEntry,
    OrderStatus,
    LedgerEntryType,
)


class WalletRepository(ABC):
    """Wallet repository interface."""
    
    @abstractmethod
    async def get_by_user_id(self, user_id: int, for_update: bool = False) -> Optional[Wallet]:
        """Get wallet by user ID."""
        ...
    
    @abstractmethod
    async def create(self, user_id: int, initial_balance: Decimal = Decimal("0")) -> Wallet:
        """Create wallet for user."""
        ...
    
    @abstractmethod
    async def update(self, wallet: Wallet) -> Wallet:
        """Update wallet."""
        ...


class PositionRepository(ABC):
    """Position repository interface."""
    
    @abstractmethod
    async def get_by_user_and_symbol(
        self, user_id: int, symbol: str, for_update: bool = False
    ) -> Optional[Position]:
        """Get position by user and symbol."""
        ...
    
    @abstractmethod
    async def get_all_by_user(self, user_id: int) -> List[Position]:
        """Get all positions for user."""
        ...
    
    @abstractmethod
    async def create(self, user_id: int, symbol: str) -> Position:
        """Create position for user."""
        ...
    
    @abstractmethod
    async def update(self, position: Position) -> Position:
        """Update position."""
        ...


class OrderRepository(ABC):
    """Order repository interface."""
    
    @abstractmethod
    async def get_by_id(self, order_id: int, for_update: bool = False) -> Optional[Order]:
        """Get order by ID."""
        ...
    
    @abstractmethod
    async def get_by_user_and_id(self, user_id: int, order_id: int) -> Optional[Order]:
        """Get order by user and ID."""
        ...
    
    @abstractmethod
    async def get_by_client_order_id(self, user_id: int, client_order_id: str) -> Optional[Order]:
        """Get order by client order ID."""
        ...
    
    @abstractmethod
    async def get_all_by_user(
        self,
        user_id: int,
        status: Optional[OrderStatus] = None,
        symbol: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Order]:
        """Get orders for user with filters."""
        ...
    
    @abstractmethod
    async def get_active_orders_by_symbol(self, symbol: str) -> List[Order]:
        """Get active orders for symbol (for matching)."""
        ...
    
    @abstractmethod
    async def create(self, order: Order) -> Order:
        """Create order."""
        ...
    
    @abstractmethod
    async def update(self, order: Order) -> Order:
        """Update order."""
        ...


class TradeRepository(ABC):
    """Trade repository interface."""
    
    @abstractmethod
    async def get_by_order_id(self, order_id: int) -> List[Trade]:
        """Get trades by order ID."""
        ...
    
    @abstractmethod
    async def get_all_by_user(
        self,
        user_id: int,
        symbol: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Trade]:
        """Get trades for user."""
        ...
    
    @abstractmethod
    async def create(self, trade: Trade) -> Trade:
        """Create trade."""
        ...


class LedgerRepository(ABC):
    """Ledger repository interface."""
    
    @abstractmethod
    async def get_all_by_user(
        self,
        user_id: int,
        entry_type: Optional[LedgerEntryType] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[LedgerEntry]:
        """Get ledger entries for user."""
        ...
    
    @abstractmethod
    async def create(self, entry: LedgerEntry) -> LedgerEntry:
        """Create ledger entry."""
        ...

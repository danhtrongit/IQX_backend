"""Symbol repository protocols."""
from typing import Protocol, Optional, List
from app.domain.symbol.entities import Symbol, Industry


class SymbolRepository(Protocol):
    """Symbol repository interface."""
    
    async def get_by_id(self, symbol_id: int) -> Optional[Symbol]:
        """Get symbol by ID."""
        ...
    
    async def get_by_symbol(self, symbol: str) -> Optional[Symbol]:
        """Get symbol by ticker code."""
        ...
    
    async def get_all(
        self,
        exchange: Optional[str] = None,
        type: Optional[str] = None,
        icb_code2: Optional[str] = None,
        is_active: Optional[bool] = True,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Symbol]:
        """Get all symbols with filters."""
        ...
    
    async def count(
        self,
        exchange: Optional[str] = None,
        type: Optional[str] = None,
        icb_code2: Optional[str] = None,
        is_active: Optional[bool] = True,
    ) -> int:
        """Count symbols with filters."""
        ...
    
    async def search(
        self,
        query: str,
        limit: int = 20,
    ) -> List[Symbol]:
        """Search symbols by name or code."""
        ...
    
    async def create(self, symbol: Symbol) -> Symbol:
        """Create a new symbol."""
        ...
    
    async def update(self, symbol: Symbol) -> Symbol:
        """Update an existing symbol."""
        ...
    
    async def upsert(self, symbol: Symbol) -> Symbol:
        """Create or update symbol."""
        ...
    
    async def bulk_upsert(self, symbols: List[Symbol]) -> int:
        """Bulk create or update symbols. Returns count."""
        ...
    
    async def symbol_exists(self, symbol: str) -> bool:
        """Check if symbol exists."""
        ...


class IndustryRepository(Protocol):
    """Industry repository interface."""
    
    async def get_by_code(self, icb_code: str) -> Optional[Industry]:
        """Get industry by ICB code."""
        ...
    
    async def get_all(self, level: Optional[int] = None) -> List[Industry]:
        """Get all industries, optionally filtered by level."""
        ...
    
    async def bulk_upsert(self, industries: List[Industry]) -> int:
        """Bulk create or update industries."""
        ...

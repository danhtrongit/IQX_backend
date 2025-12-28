"""Symbol domain errors."""
from app.core.errors import NotFoundError, ConflictError


class SymbolNotFoundError(NotFoundError):
    """Symbol not found."""
    
    def __init__(self, identifier: str | int | None = None):
        super().__init__("Symbol", identifier)


class SymbolAlreadyExistsError(ConflictError):
    """Symbol already exists."""
    
    def __init__(self, symbol: str):
        super().__init__(
            message=f"Symbol '{symbol}' already exists",
            details={"symbol": symbol},
        )


class IndustryNotFoundError(NotFoundError):
    """Industry not found."""
    
    def __init__(self, identifier: str | int | None = None):
        super().__init__("Industry", identifier)

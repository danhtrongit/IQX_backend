"""Trading domain errors."""
from app.core.errors import AppError


class TradingError(AppError):
    """Base trading error."""
    pass


class InsufficientBalanceError(TradingError):
    """Insufficient balance for order."""
    
    def __init__(self, required: float, available: float):
        super().__init__(
            code="INSUFFICIENT_BALANCE",
            message=f"Insufficient balance. Required: {required:,.0f}, Available: {available:,.0f}",
            details={"required": required, "available": available},
        )


class InsufficientPositionError(TradingError):
    """Insufficient position for sell order."""
    
    def __init__(self, symbol: str, required: float, available: float):
        super().__init__(
            code="INSUFFICIENT_POSITION",
            message=f"Insufficient position for {symbol}. Required: {required}, Available: {available}",
            details={"symbol": symbol, "required": required, "available": available},
        )


class InvalidOrderError(TradingError):
    """Invalid order parameters."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            code="INVALID_ORDER",
            message=message,
            details=details or {},
        )


class OrderNotFoundError(TradingError):
    """Order not found."""
    
    def __init__(self, order_id: int):
        super().__init__(
            code="ORDER_NOT_FOUND",
            message=f"Order {order_id} not found",
            details={"order_id": order_id},
        )


class OrderNotCancelableError(TradingError):
    """Order cannot be canceled."""
    
    def __init__(self, order_id: int, status: str):
        super().__init__(
            code="ORDER_NOT_CANCELABLE",
            message=f"Order {order_id} cannot be canceled. Status: {status}",
            details={"order_id": order_id, "status": status},
        )


class MarketPriceNotFoundError(TradingError):
    """Market price not found for symbol."""
    
    def __init__(self, symbol: str):
        super().__init__(
            code="MARKET_PRICE_NOT_FOUND",
            message=f"Market price not found for {symbol}",
            details={"symbol": symbol},
        )


class DuplicateClientOrderIdError(TradingError):
    """Duplicate client order ID."""
    
    def __init__(self, client_order_id: str):
        super().__init__(
            code="DUPLICATE_CLIENT_ORDER_ID",
            message=f"Duplicate client order ID: {client_order_id}",
            details={"client_order_id": client_order_id},
        )

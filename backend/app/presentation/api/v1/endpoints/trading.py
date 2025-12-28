"""Trading endpoints."""
from typing import Optional
from fastapi import APIRouter, Query, Path

from app.application.trading.dtos import (
    PlaceOrderRequest,
    OrderListRequest,
    TradeListRequest,
    LedgerListRequest,
    WalletResponse,
    PositionListResponse,
    OrderResponse,
    OrderListResponse,
    PlaceOrderResponse,
    CancelOrderResponse,
    TradeListResponse,
    LedgerListResponse,
    GrantCashResponse,
)
from app.application.trading.services import TradingService
from app.infrastructure.repositories.trading_repo import (
    SQLAlchemyWalletRepository,
    SQLAlchemyPositionRepository,
    SQLAlchemyOrderRepository,
    SQLAlchemyTradeRepository,
    SQLAlchemyLedgerRepository,
)
from app.infrastructure.trading.price_provider import VnstockMarketPriceProvider
from app.presentation.deps.auth_deps import CurrentUser, DBSession

router = APIRouter(prefix="/trading", tags=["Trading"])


def get_trading_service(db: DBSession) -> TradingService:
    """Create trading service with dependencies."""
    return TradingService(
        wallet_repo=SQLAlchemyWalletRepository(db),
        position_repo=SQLAlchemyPositionRepository(db),
        order_repo=SQLAlchemyOrderRepository(db),
        trade_repo=SQLAlchemyTradeRepository(db),
        ledger_repo=SQLAlchemyLedgerRepository(db),
        price_provider=VnstockMarketPriceProvider(),
    )


# === Wallet & Portfolio ===

@router.get("/wallet", response_model=WalletResponse)
async def get_wallet(
    db: DBSession,
    current_user: CurrentUser,
) -> WalletResponse:
    """
    Get current user's wallet.
    
    Returns balance, locked amount, and available balance.
    """
    service = get_trading_service(db)
    return await service.get_wallet(current_user.id)


@router.get("/positions", response_model=PositionListResponse)
async def get_positions(
    db: DBSession,
    current_user: CurrentUser,
) -> PositionListResponse:
    """
    Get current user's positions (stock holdings).
    
    Returns list of positions with:
    - Quantity and locked quantity
    - Average price
    - Current market price and value
    - Unrealized P&L
    """
    service = get_trading_service(db)
    return await service.get_positions(current_user.id)


# === Bootstrap ===

@router.post("/bootstrap/grant-initial-cash", response_model=GrantCashResponse)
async def grant_initial_cash(
    db: DBSession,
    current_user: CurrentUser,
) -> GrantCashResponse:
    """
    Grant initial cash (1,000,000,000 VND) to user.
    
    This is idempotent - calling multiple times will only grant once.
    """
    service = get_trading_service(db)
    return await service.grant_initial_cash(current_user.id)


# === Orders ===

@router.post("/orders", response_model=PlaceOrderResponse)
async def place_order(
    request: PlaceOrderRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> PlaceOrderResponse:
    """
    Place a new order.
    
    **Order Types:**
    - MARKET: Execute immediately at current market price
    - LIMIT: Execute when market price reaches limit price
    
    **Sides:**
    - BUY: Purchase shares (requires sufficient balance)
    - SELL: Sell shares (requires sufficient position)
    
    **Fee:** 0.1% of trade value
    
    **T0 Settlement:** Orders are settled immediately (no T+2)
    """
    service = get_trading_service(db)
    return await service.place_order(current_user.id, request)


@router.get("/orders", response_model=OrderListResponse)
async def get_orders(
    db: DBSession,
    current_user: CurrentUser,
    status: Optional[str] = Query(None, description="Filter by status: NEW, FILLED, CANCELED, etc."),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> OrderListResponse:
    """
    Get user's orders with optional filters.
    """
    service = get_trading_service(db)
    request = OrderListRequest(status=status, symbol=symbol, limit=limit, offset=offset)
    return await service.get_orders(current_user.id, request)


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int = Path(..., description="Order ID"),
    db: DBSession = None,
    current_user: CurrentUser = None,
) -> OrderResponse:
    """
    Get order detail by ID.
    
    Includes list of trades (fills) if order has been executed.
    """
    service = get_trading_service(db)
    return await service.get_order(current_user.id, order_id)


@router.post("/orders/{order_id}/cancel", response_model=CancelOrderResponse)
async def cancel_order(
    order_id: int = Path(..., description="Order ID"),
    db: DBSession = None,
    current_user: CurrentUser = None,
) -> CancelOrderResponse:
    """
    Cancel an order.
    
    Only NEW or PARTIALLY_FILLED orders can be canceled.
    Locked funds/shares will be released.
    """
    service = get_trading_service(db)
    return await service.cancel_order(current_user.id, order_id)


# === Trades ===

@router.get("/trades", response_model=TradeListResponse)
async def get_trades(
    db: DBSession,
    current_user: CurrentUser,
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> TradeListResponse:
    """
    Get user's trade history.
    
    Returns list of executed trades with price, quantity, fee, and value.
    """
    service = get_trading_service(db)
    request = TradeListRequest(symbol=symbol, limit=limit, offset=offset)
    return await service.get_trades(current_user.id, request)


# === Ledger ===

@router.get("/ledger", response_model=LedgerListResponse)
async def get_ledger(
    db: DBSession,
    current_user: CurrentUser,
    entry_type: Optional[str] = Query(None, description="Filter by type: GRANT, BUY, SELL, FEE, LOCK, UNLOCK"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> LedgerListResponse:
    """
    Get user's ledger (transaction history).
    
    Returns all balance changes with audit trail.
    """
    service = get_trading_service(db)
    request = LedgerListRequest(entry_type=entry_type, limit=limit, offset=offset)
    return await service.get_ledger(current_user.id, request)

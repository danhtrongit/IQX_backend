"""Trading application services."""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from app.core.config import settings
from app.core.logging import get_logger
from app.domain.trading.entities import (
    Wallet,
    Position,
    Order,
    Trade,
    LedgerEntry,
    OrderSide,
    OrderType,
    OrderStatus,
    LedgerEntryType,
)
from app.domain.trading.repositories import (
    WalletRepository,
    PositionRepository,
    OrderRepository,
    TradeRepository,
    LedgerRepository,
)
from app.domain.trading.errors import (
    InsufficientBalanceError,
    InsufficientPositionError,
    InvalidOrderError,
    OrderNotFoundError,
    OrderNotCancelableError,
    MarketPriceNotFoundError,
    DuplicateClientOrderIdError,
)
from app.application.trading.dtos import (
    PlaceOrderRequest,
    OrderListRequest,
    TradeListRequest,
    LedgerListRequest,
    WalletResponse,
    PositionResponse,
    PositionListResponse,
    OrderResponse,
    OrderListResponse,
    PlaceOrderResponse,
    CancelOrderResponse,
    TradeResponse,
    TradeListResponse,
    LedgerEntryResponse,
    LedgerListResponse,
    GrantCashResponse,
)

logger = get_logger(__name__)

# Constants
INITIAL_CASH = Decimal("1000000000")  # 1 billion VND
FEE_RATE = Decimal("0.001")  # 0.1%


class MarketPriceProvider:
    """Interface for getting market prices."""
    
    async def get_price(self, symbol: str) -> Optional[Decimal]:
        """Get current market price for symbol."""
        raise NotImplementedError


class TradingService:
    """Trading service - handles all trading operations."""
    
    def __init__(
        self,
        wallet_repo: WalletRepository,
        position_repo: PositionRepository,
        order_repo: OrderRepository,
        trade_repo: TradeRepository,
        ledger_repo: LedgerRepository,
        price_provider: MarketPriceProvider,
    ):
        self.wallet_repo = wallet_repo
        self.position_repo = position_repo
        self.order_repo = order_repo
        self.trade_repo = trade_repo
        self.ledger_repo = ledger_repo
        self.price_provider = price_provider
    
    # === Wallet Operations ===
    
    async def get_or_create_wallet(self, user_id: int) -> Wallet:
        """Get or create wallet for user."""
        wallet = await self.wallet_repo.get_by_user_id(user_id)
        if not wallet:
            wallet = await self.wallet_repo.create(user_id)
        return wallet
    
    async def grant_initial_cash(self, user_id: int) -> GrantCashResponse:
        """Grant initial cash to user (idempotent)."""
        wallet = await self.wallet_repo.get_by_user_id(user_id, for_update=True)
        
        if not wallet:
            wallet = await self.wallet_repo.create(user_id, INITIAL_CASH)
            wallet.first_grant_at = datetime.utcnow()
            wallet = await self.wallet_repo.update(wallet)
            
            # Create ledger entry
            await self.ledger_repo.create(LedgerEntry(
                id=0,
                user_id=user_id,
                entry_type=LedgerEntryType.GRANT,
                amount=INITIAL_CASH,
                balance_after=wallet.balance,
                ref_type="SYSTEM",
                meta_json={"reason": "initial_grant"},
            ))
            
            return GrantCashResponse(
                wallet=self._wallet_to_response(wallet),
                granted=True,
                message=f"Granted {INITIAL_CASH:,.0f} VND to your account",
            )
        
        if wallet.first_grant_at:
            return GrantCashResponse(
                wallet=self._wallet_to_response(wallet),
                granted=False,
                message="Initial cash already granted",
            )
        
        # Grant cash
        wallet.balance += INITIAL_CASH
        wallet.first_grant_at = datetime.utcnow()
        wallet = await self.wallet_repo.update(wallet)
        
        # Create ledger entry
        await self.ledger_repo.create(LedgerEntry(
            id=0,
            user_id=user_id,
            entry_type=LedgerEntryType.GRANT,
            amount=INITIAL_CASH,
            balance_after=wallet.balance,
            ref_type="SYSTEM",
            meta_json={"reason": "initial_grant"},
        ))
        
        return GrantCashResponse(
            wallet=self._wallet_to_response(wallet),
            granted=True,
            message=f"Granted {INITIAL_CASH:,.0f} VND to your account",
        )
    
    async def get_wallet(self, user_id: int) -> WalletResponse:
        """Get user wallet."""
        wallet = await self.get_or_create_wallet(user_id)
        return self._wallet_to_response(wallet)
    
    # === Position Operations ===
    
    async def get_positions(self, user_id: int) -> PositionListResponse:
        """Get all positions for user."""
        positions = await self.position_repo.get_all_by_user(user_id)
        
        items = []
        total_value = Decimal("0")
        
        for pos in positions:
            market_price = await self.price_provider.get_price(pos.symbol)
            market_value = None
            unrealized_pnl = None
            
            if market_price and pos.quantity > 0:
                market_value = pos.quantity * market_price
                cost_basis = pos.quantity * pos.avg_price
                unrealized_pnl = market_value - cost_basis
                total_value += market_value
            
            items.append(PositionResponse(
                symbol=pos.symbol,
                quantity=pos.quantity,
                locked_quantity=pos.locked_quantity,
                available_quantity=pos.available_quantity,
                avg_price=pos.avg_price,
                market_price=market_price,
                market_value=market_value,
                unrealized_pnl=unrealized_pnl,
            ))
        
        return PositionListResponse(
            data=items,
            total_market_value=total_value if total_value > 0 else None,
        )
    
    # === Order Operations ===
    
    async def place_order(self, user_id: int, request: PlaceOrderRequest) -> PlaceOrderResponse:
        """Place a new order."""
        symbol = request.symbol.upper()
        side = OrderSide(request.side)
        order_type = OrderType(request.type)
        quantity = request.quantity
        limit_price = request.limit_price
        
        # Validate limit price for LIMIT orders
        if order_type == OrderType.LIMIT and not limit_price:
            raise InvalidOrderError("Limit price required for LIMIT orders")
        
        # Check duplicate client_order_id
        if request.client_order_id:
            existing = await self.order_repo.get_by_client_order_id(user_id, request.client_order_id)
            if existing:
                raise DuplicateClientOrderIdError(request.client_order_id)
        
        # Get market price
        market_price = await self.price_provider.get_price(symbol)
        if not market_price:
            raise MarketPriceNotFoundError(symbol)
        
        # Determine execution price
        exec_price = limit_price if order_type == OrderType.LIMIT else market_price
        
        # Get wallet with lock
        wallet = await self.wallet_repo.get_by_user_id(user_id, for_update=True)
        if not wallet:
            wallet = await self.wallet_repo.create(user_id)
        
        # Calculate required amount
        fee = quantity * exec_price * FEE_RATE
        
        if side == OrderSide.BUY:
            required = quantity * exec_price + fee
            if wallet.available < required:
                raise InsufficientBalanceError(float(required), float(wallet.available))
            
            # Lock funds
            wallet.lock(required)
            await self.wallet_repo.update(wallet)
            
            # Create ledger entry for lock
            await self.ledger_repo.create(LedgerEntry(
                id=0,
                user_id=user_id,
                entry_type=LedgerEntryType.LOCK,
                amount=-required,
                balance_after=wallet.available,
                ref_type="ORDER",
                meta_json={"symbol": symbol, "side": "BUY", "quantity": float(quantity)},
            ))
        else:  # SELL
            position = await self.position_repo.get_by_user_and_symbol(user_id, symbol, for_update=True)
            if not position or position.available_quantity < quantity:
                available = position.available_quantity if position else Decimal("0")
                raise InsufficientPositionError(symbol, float(quantity), float(available))
            
            # Lock shares
            position.lock(quantity)
            await self.position_repo.update(position)
        
        # Create order
        order = Order(
            id=0,
            user_id=user_id,
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity,
            limit_price=limit_price,
            status=OrderStatus.NEW,
            price_snapshot=market_price,
            client_order_id=request.client_order_id,
        )
        order = await self.order_repo.create(order)
        
        # Try to execute immediately
        trades = await self._try_execute_order(order, market_price)
        
        # Refresh wallet
        wallet = await self.wallet_repo.get_by_user_id(user_id)
        
        return PlaceOrderResponse(
            order=await self._order_to_response(order, trades),
            wallet=self._wallet_to_response(wallet),
        )
    
    async def _try_execute_order(self, order: Order, market_price: Decimal) -> List[Trade]:
        """Try to execute order based on market price."""
        trades = []
        
        # Check if order can be filled
        can_fill = False
        if order.type == OrderType.MARKET:
            can_fill = True
        elif order.type == OrderType.LIMIT:
            if order.side == OrderSide.BUY and order.limit_price >= market_price:
                can_fill = True
            elif order.side == OrderSide.SELL and order.limit_price <= market_price:
                can_fill = True
        
        if not can_fill:
            return trades
        
        # Execute at market price (or limit price for limit orders)
        exec_price = market_price
        if order.type == OrderType.LIMIT:
            exec_price = order.limit_price if order.side == OrderSide.BUY else market_price
        
        qty = order.remaining_quantity
        fee = qty * exec_price * FEE_RATE
        
        # Create trade
        trade = Trade(
            id=0,
            order_id=order.id,
            user_id=order.user_id,
            symbol=order.symbol,
            side=order.side,
            quantity=qty,
            price=exec_price,
            fee=fee,
        )
        trade = await self.trade_repo.create(trade)
        trades.append(trade)
        
        # Update order
        order.fill(qty, exec_price, fee)
        await self.order_repo.update(order)
        
        # Update wallet and position
        wallet = await self.wallet_repo.get_by_user_id(order.user_id, for_update=True)
        
        if order.side == OrderSide.BUY:
            # Deduct from locked and balance
            total_cost = qty * exec_price + fee
            wallet.locked -= total_cost
            wallet.deduct(total_cost)
            await self.wallet_repo.update(wallet)
            
            # Add to position
            position = await self.position_repo.get_by_user_and_symbol(
                order.user_id, order.symbol, for_update=True
            )
            if not position:
                position = await self.position_repo.create(order.user_id, order.symbol)
            
            # Update avg price and quantity
            if position.quantity == Decimal("0"):
                position.avg_price = exec_price
                position.quantity = qty
            else:
                total_value = position.quantity * position.avg_price + qty * exec_price
                position.quantity += qty
                position.avg_price = total_value / position.quantity
            
            await self.position_repo.update(position)
            
            # Ledger entries
            await self.ledger_repo.create(LedgerEntry(
                id=0,
                user_id=order.user_id,
                entry_type=LedgerEntryType.BUY,
                amount=-(qty * exec_price),
                balance_after=wallet.balance,
                ref_type="TRADE",
                ref_id=trade.id,
                meta_json={"symbol": order.symbol, "quantity": float(qty), "price": float(exec_price)},
            ))
            await self.ledger_repo.create(LedgerEntry(
                id=0,
                user_id=order.user_id,
                entry_type=LedgerEntryType.FEE,
                amount=-fee,
                balance_after=wallet.balance,
                ref_type="TRADE",
                ref_id=trade.id,
            ))
        else:  # SELL
            # Credit proceeds minus fee
            proceeds = qty * exec_price - fee
            wallet.credit(proceeds)
            await self.wallet_repo.update(wallet)
            
            # Remove from position
            position = await self.position_repo.get_by_user_and_symbol(
                order.user_id, order.symbol, for_update=True
            )
            position.locked_quantity -= qty
            position.quantity -= qty
            if position.quantity <= Decimal("0"):
                position.quantity = Decimal("0")
                position.avg_price = Decimal("0")
            await self.position_repo.update(position)
            
            # Ledger entries
            await self.ledger_repo.create(LedgerEntry(
                id=0,
                user_id=order.user_id,
                entry_type=LedgerEntryType.SELL,
                amount=qty * exec_price,
                balance_after=wallet.balance + fee,
                ref_type="TRADE",
                ref_id=trade.id,
                meta_json={"symbol": order.symbol, "quantity": float(qty), "price": float(exec_price)},
            ))
            await self.ledger_repo.create(LedgerEntry(
                id=0,
                user_id=order.user_id,
                entry_type=LedgerEntryType.FEE,
                amount=-fee,
                balance_after=wallet.balance,
                ref_type="TRADE",
                ref_id=trade.id,
            ))
        
        return trades
    
    async def cancel_order(self, user_id: int, order_id: int) -> CancelOrderResponse:
        """Cancel an order."""
        order = await self.order_repo.get_by_user_and_id(user_id, order_id)
        if not order:
            raise OrderNotFoundError(order_id)
        
        if not order.can_cancel():
            raise OrderNotCancelableError(order_id, order.status.value)
        
        # Get order with lock
        order = await self.order_repo.get_by_id(order_id, for_update=True)
        
        # Release locks
        remaining_qty = order.remaining_quantity
        
        if order.side == OrderSide.BUY:
            # Release locked funds
            wallet = await self.wallet_repo.get_by_user_id(user_id, for_update=True)
            exec_price = order.limit_price or order.price_snapshot
            release_amount = remaining_qty * exec_price * (1 + FEE_RATE)
            wallet.unlock(release_amount)
            await self.wallet_repo.update(wallet)
            
            # Ledger entry
            await self.ledger_repo.create(LedgerEntry(
                id=0,
                user_id=user_id,
                entry_type=LedgerEntryType.CANCEL_RELEASE,
                amount=release_amount,
                balance_after=wallet.available,
                ref_type="ORDER",
                ref_id=order_id,
            ))
        else:  # SELL
            # Release locked shares
            position = await self.position_repo.get_by_user_and_symbol(
                user_id, order.symbol, for_update=True
            )
            if position:
                position.unlock(remaining_qty)
                await self.position_repo.update(position)
        
        # Cancel order
        order.cancel()
        await self.order_repo.update(order)
        
        # Get updated wallet
        wallet = await self.wallet_repo.get_by_user_id(user_id)
        
        return CancelOrderResponse(
            order=await self._order_to_response(order),
            wallet=self._wallet_to_response(wallet),
        )
    
    async def get_orders(self, user_id: int, request: OrderListRequest) -> OrderListResponse:
        """Get orders for user."""
        status = None
        if request.status:
            try:
                status = OrderStatus(request.status.upper())
            except ValueError:
                pass  # Invalid status, ignore filter
        
        orders = await self.order_repo.get_all_by_user(
            user_id,
            status=status,
            symbol=request.symbol,
            limit=request.limit,
            offset=request.offset,
        )
        
        items = [await self._order_to_response(o) for o in orders]
        return OrderListResponse(data=items, count=len(items))
    
    async def get_order(self, user_id: int, order_id: int) -> OrderResponse:
        """Get order detail."""
        order = await self.order_repo.get_by_user_and_id(user_id, order_id)
        if not order:
            raise OrderNotFoundError(order_id)
        
        trades = await self.trade_repo.get_by_order_id(order_id)
        return await self._order_to_response(order, trades)
    
    # === Trade Operations ===
    
    async def get_trades(self, user_id: int, request: TradeListRequest) -> TradeListResponse:
        """Get trades for user."""
        trades = await self.trade_repo.get_all_by_user(
            user_id,
            symbol=request.symbol,
            limit=request.limit,
            offset=request.offset,
        )
        
        items = [self._trade_to_response(t) for t in trades]
        return TradeListResponse(data=items, count=len(items))
    
    # === Ledger Operations ===
    
    async def get_ledger(self, user_id: int, request: LedgerListRequest) -> LedgerListResponse:
        """Get ledger entries for user."""
        entry_type = None
        if request.entry_type:
            try:
                entry_type = LedgerEntryType(request.entry_type.upper())
            except ValueError:
                pass  # Invalid entry_type, ignore filter
        
        entries = await self.ledger_repo.get_all_by_user(
            user_id,
            entry_type=entry_type,
            limit=request.limit,
            offset=request.offset,
        )
        
        items = [self._ledger_to_response(e) for e in entries]
        return LedgerListResponse(data=items, count=len(items))
    
    # === Response Converters ===
    
    def _wallet_to_response(self, wallet: Wallet) -> WalletResponse:
        return WalletResponse(
            balance=wallet.balance,
            locked=wallet.locked,
            available=wallet.available,
            currency=wallet.currency,
            first_grant_at=wallet.first_grant_at,
        )
    
    async def _order_to_response(
        self, order: Order, trades: List[Trade] = None
    ) -> OrderResponse:
        trade_responses = None
        if trades:
            trade_responses = [self._trade_to_response(t) for t in trades]
        
        return OrderResponse(
            id=order.id,
            symbol=order.symbol,
            side=order.side.value,
            type=order.type.value,
            quantity=order.quantity,
            limit_price=order.limit_price,
            status=order.status.value,
            filled_quantity=order.filled_quantity,
            remaining_quantity=order.remaining_quantity,
            avg_filled_price=order.avg_filled_price,
            fee_total=order.fee_total,
            price_snapshot=order.price_snapshot,
            client_order_id=order.client_order_id,
            created_at=order.created_at,
            updated_at=order.updated_at,
            canceled_at=order.canceled_at,
            trades=trade_responses,
        )
    
    def _trade_to_response(self, trade: Trade) -> TradeResponse:
        return TradeResponse(
            id=trade.id,
            order_id=trade.order_id,
            symbol=trade.symbol,
            side=trade.side.value,
            quantity=trade.quantity,
            price=trade.price,
            fee=trade.fee,
            value=trade.quantity * trade.price,
            executed_at=trade.executed_at,
        )
    
    def _ledger_to_response(self, entry: LedgerEntry) -> LedgerEntryResponse:
        return LedgerEntryResponse(
            id=entry.id,
            entry_type=entry.entry_type.value,
            amount=entry.amount,
            balance_after=entry.balance_after,
            ref_type=entry.ref_type,
            ref_id=entry.ref_id,
            meta=entry.meta_json,
            created_at=entry.created_at,
        )

"""Trading repository implementations."""
from decimal import Decimal
from typing import Optional, List
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.infrastructure.models.trading_model import (
    WalletModel,
    PositionModel,
    OrderModel,
    TradeModel,
    LedgerEntryModel,
)


class SQLAlchemyWalletRepository(WalletRepository):
    """SQLAlchemy wallet repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _to_entity(self, model: WalletModel) -> Wallet:
        return Wallet(
            id=model.id,
            user_id=model.user_id,
            balance=model.balance,
            locked=model.locked,
            currency=model.currency,
            first_grant_at=model.first_grant_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    async def get_by_user_id(self, user_id: int, for_update: bool = False) -> Optional[Wallet]:
        stmt = select(WalletModel).where(WalletModel.user_id == user_id)
        if for_update:
            stmt = stmt.with_for_update()
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
    
    async def create(self, user_id: int, initial_balance: Decimal = Decimal("0")) -> Wallet:
        model = WalletModel(
            user_id=user_id,
            balance=initial_balance,
            locked=Decimal("0"),
            currency="VND",
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)
    
    async def update(self, wallet: Wallet) -> Wallet:
        stmt = select(WalletModel).where(WalletModel.id == wallet.id).with_for_update()
        result = await self.session.execute(stmt)
        model = result.scalar_one()
        model.balance = wallet.balance
        model.locked = wallet.locked
        model.first_grant_at = wallet.first_grant_at
        model.updated_at = datetime.utcnow()
        await self.session.flush()
        return self._to_entity(model)


class SQLAlchemyPositionRepository(PositionRepository):
    """SQLAlchemy position repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _to_entity(self, model: PositionModel) -> Position:
        return Position(
            id=model.id,
            user_id=model.user_id,
            symbol=model.symbol,
            quantity=model.quantity,
            locked_quantity=model.locked_quantity,
            avg_price=model.avg_price,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    async def get_by_user_and_symbol(
        self, user_id: int, symbol: str, for_update: bool = False
    ) -> Optional[Position]:
        stmt = select(PositionModel).where(
            and_(PositionModel.user_id == user_id, PositionModel.symbol == symbol.upper())
        )
        if for_update:
            stmt = stmt.with_for_update()
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
    
    async def get_all_by_user(self, user_id: int) -> List[Position]:
        stmt = select(PositionModel).where(
            and_(PositionModel.user_id == user_id, PositionModel.quantity > 0)
        ).order_by(PositionModel.symbol)
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]
    
    async def create(self, user_id: int, symbol: str) -> Position:
        model = PositionModel(
            user_id=user_id,
            symbol=symbol.upper(),
            quantity=Decimal("0"),
            locked_quantity=Decimal("0"),
            avg_price=Decimal("0"),
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)
    
    async def update(self, position: Position) -> Position:
        stmt = select(PositionModel).where(PositionModel.id == position.id).with_for_update()
        result = await self.session.execute(stmt)
        model = result.scalar_one()
        model.quantity = position.quantity
        model.locked_quantity = position.locked_quantity
        model.avg_price = position.avg_price
        model.updated_at = datetime.utcnow()
        await self.session.flush()
        return self._to_entity(model)


class SQLAlchemyOrderRepository(OrderRepository):
    """SQLAlchemy order repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _to_entity(self, model: OrderModel) -> Order:
        return Order(
            id=model.id,
            user_id=model.user_id,
            symbol=model.symbol,
            side=OrderSide(model.side),
            type=OrderType(model.type),
            quantity=model.quantity,
            limit_price=model.limit_price,
            status=OrderStatus(model.status),
            filled_quantity=model.filled_quantity,
            avg_filled_price=model.avg_filled_price,
            fee_total=model.fee_total,
            price_snapshot=model.price_snapshot,
            client_order_id=model.client_order_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            canceled_at=model.canceled_at,
        )
    
    async def get_by_id(self, order_id: int, for_update: bool = False) -> Optional[Order]:
        stmt = select(OrderModel).where(OrderModel.id == order_id)
        if for_update:
            stmt = stmt.with_for_update()
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
    
    async def get_by_user_and_id(self, user_id: int, order_id: int) -> Optional[Order]:
        stmt = select(OrderModel).where(
            and_(OrderModel.user_id == user_id, OrderModel.id == order_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
    
    async def get_by_client_order_id(self, user_id: int, client_order_id: str) -> Optional[Order]:
        stmt = select(OrderModel).where(
            and_(OrderModel.user_id == user_id, OrderModel.client_order_id == client_order_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
    
    async def get_all_by_user(
        self,
        user_id: int,
        status: Optional[OrderStatus] = None,
        symbol: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Order]:
        stmt = select(OrderModel).where(OrderModel.user_id == user_id)
        if status:
            stmt = stmt.where(OrderModel.status == status.value)
        if symbol:
            stmt = stmt.where(OrderModel.symbol == symbol.upper())
        stmt = stmt.order_by(OrderModel.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]
    
    async def get_active_orders_by_symbol(self, symbol: str) -> List[Order]:
        stmt = select(OrderModel).where(
            and_(
                OrderModel.symbol == symbol.upper(),
                OrderModel.status.in_([OrderStatus.NEW.value, OrderStatus.PARTIALLY_FILLED.value]),
            )
        ).order_by(OrderModel.created_at)
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]
    
    async def create(self, order: Order) -> Order:
        model = OrderModel(
            user_id=order.user_id,
            symbol=order.symbol.upper(),
            side=order.side.value,
            type=order.type.value,
            quantity=order.quantity,
            limit_price=order.limit_price,
            status=order.status.value,
            filled_quantity=order.filled_quantity,
            avg_filled_price=order.avg_filled_price,
            fee_total=order.fee_total,
            price_snapshot=order.price_snapshot,
            client_order_id=order.client_order_id,
        )
        self.session.add(model)
        await self.session.flush()
        order.id = model.id
        order.created_at = model.created_at
        return order
    
    async def update(self, order: Order) -> Order:
        stmt = select(OrderModel).where(OrderModel.id == order.id).with_for_update()
        result = await self.session.execute(stmt)
        model = result.scalar_one()
        model.status = order.status.value
        model.filled_quantity = order.filled_quantity
        model.avg_filled_price = order.avg_filled_price
        model.fee_total = order.fee_total
        model.canceled_at = order.canceled_at
        model.updated_at = datetime.utcnow()
        await self.session.flush()
        return order


class SQLAlchemyTradeRepository(TradeRepository):
    """SQLAlchemy trade repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _to_entity(self, model: TradeModel) -> Trade:
        return Trade(
            id=model.id,
            order_id=model.order_id,
            user_id=model.user_id,
            symbol=model.symbol,
            side=OrderSide(model.side),
            quantity=model.quantity,
            price=model.price,
            fee=model.fee,
            executed_at=model.executed_at,
        )
    
    async def get_by_order_id(self, order_id: int) -> List[Trade]:
        stmt = select(TradeModel).where(TradeModel.order_id == order_id).order_by(TradeModel.executed_at)
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]
    
    async def get_all_by_user(
        self,
        user_id: int,
        symbol: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Trade]:
        stmt = select(TradeModel).where(TradeModel.user_id == user_id)
        if symbol:
            stmt = stmt.where(TradeModel.symbol == symbol.upper())
        stmt = stmt.order_by(TradeModel.executed_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]
    
    async def create(self, trade: Trade) -> Trade:
        model = TradeModel(
            order_id=trade.order_id,
            user_id=trade.user_id,
            symbol=trade.symbol.upper(),
            side=trade.side.value,
            quantity=trade.quantity,
            price=trade.price,
            fee=trade.fee,
        )
        self.session.add(model)
        await self.session.flush()
        trade.id = model.id
        trade.executed_at = model.executed_at
        return trade


class SQLAlchemyLedgerRepository(LedgerRepository):
    """SQLAlchemy ledger repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _to_entity(self, model: LedgerEntryModel) -> LedgerEntry:
        return LedgerEntry(
            id=model.id,
            user_id=model.user_id,
            entry_type=LedgerEntryType(model.entry_type),
            amount=model.amount,
            balance_after=model.balance_after,
            ref_type=model.ref_type,
            ref_id=model.ref_id,
            meta_json=model.meta_json,
            created_at=model.created_at,
        )
    
    async def get_all_by_user(
        self,
        user_id: int,
        entry_type: Optional[LedgerEntryType] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[LedgerEntry]:
        stmt = select(LedgerEntryModel).where(LedgerEntryModel.user_id == user_id)
        if entry_type:
            stmt = stmt.where(LedgerEntryModel.entry_type == entry_type.value)
        stmt = stmt.order_by(LedgerEntryModel.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]
    
    async def create(self, entry: LedgerEntry) -> LedgerEntry:
        model = LedgerEntryModel(
            user_id=entry.user_id,
            entry_type=entry.entry_type.value,
            amount=entry.amount,
            balance_after=entry.balance_after,
            ref_type=entry.ref_type,
            ref_id=entry.ref_id,
            meta_json=entry.meta_json,
        )
        self.session.add(model)
        await self.session.flush()
        entry.id = model.id
        entry.created_at = model.created_at
        return entry

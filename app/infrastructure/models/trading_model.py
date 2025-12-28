"""Trading SQLAlchemy models."""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    BigInteger,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class WalletModel(Base):
    """Wallet database model."""
    
    __tablename__ = "wallets"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    balance: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0"))
    locked: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0"))
    currency: Mapped[str] = mapped_column(String(10), default="VND")
    first_grant_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("UserModel", back_populates="wallet")


class PositionModel(Base):
    """Position database model."""
    
    __tablename__ = "positions"
    __table_args__ = (
        Index("ix_positions_user_symbol", "user_id", "symbol", unique=True),
    )
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    symbol: Mapped[str] = mapped_column(String(20))
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=Decimal("0"))
    locked_quantity: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=Decimal("0"))
    avg_price: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=Decimal("0"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OrderModel(Base):
    """Order database model."""
    
    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_orders_client_order_id", "user_id", "client_order_id", unique=True),
    )
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    side: Mapped[str] = mapped_column(String(4))
    type: Mapped[str] = mapped_column(String(10))
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    limit_price: Mapped[Decimal | None] = mapped_column(Numeric(20, 4), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="NEW", index=True)
    filled_quantity: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=Decimal("0"))
    avg_filled_price: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=Decimal("0"))
    fee_total: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=Decimal("0"))
    price_snapshot: Mapped[Decimal | None] = mapped_column(Numeric(20, 4), nullable=True)
    client_order_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    canceled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    trades = relationship("TradeModel", back_populates="order")


class TradeModel(Base):
    """Trade database model."""
    
    __tablename__ = "trades"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    symbol: Mapped[str] = mapped_column(String(20))
    side: Mapped[str] = mapped_column(String(4))
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    price: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    fee: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=Decimal("0"))
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    order = relationship("OrderModel", back_populates="trades")


class LedgerEntryModel(Base):
    """Ledger entry database model."""
    
    __tablename__ = "ledger_entries"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    entry_type: Mapped[str] = mapped_column(String(30), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    balance_after: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    ref_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    ref_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    meta_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

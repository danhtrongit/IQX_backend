"""Watchlist ORM model."""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    BigInteger,
    String,
    Text,
    Boolean,
    DateTime,
    Float,
    Integer,
    ForeignKey,
    Index,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.base import Base


class WatchlistModel(Base):
    """Watchlist database model."""

    __tablename__ = "watchlist"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    alert_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", backref="watchlist_items")

    __table_args__ = (
        UniqueConstraint("user_id", "symbol", name="uq_watchlist_user_symbol"),
        Index("ix_watchlist_user_id", "user_id"),
        Index("ix_watchlist_symbol", "symbol"),
        Index("ix_watchlist_user_position", "user_id", "position"),
    )

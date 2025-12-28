"""Symbol ORM models."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    BigInteger,
    String,
    Text,
    Boolean,
    DateTime,
    Numeric,
    Integer,
    Index,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.base import Base


class SymbolModel(Base):
    """Symbol database model."""
    
    __tablename__ = "symbols"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    organ_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    en_organ_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    organ_short_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    exchange: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # ICB Industry Classification
    icb_code1: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    icb_code2: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    icb_code3: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    icb_code4: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    icb_name2: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    icb_name3: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    icb_name4: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Company details
    company_profile: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    history: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    issue_share: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2), nullable=True)
    charter_capital: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2), nullable=True)
    
    # Metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
    
    __table_args__ = (
        Index("ix_symbols_exchange", "exchange"),
        Index("ix_symbols_type", "type"),
        Index("ix_symbols_icb_code2", "icb_code2"),
        Index("ix_symbols_is_active", "is_active"),
        # Composite indexes for common query patterns
        Index("ix_symbols_exchange_type_active", "exchange", "type", "is_active"),
        Index("ix_symbols_exchange_active", "exchange", "is_active"),
        Index("ix_symbols_type_active", "type", "is_active"),
    )


class IndustryModel(Base):
    """ICB Industry database model."""
    
    __tablename__ = "industries"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    icb_code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    icb_name: Mapped[str] = mapped_column(String(100), nullable=False)
    en_icb_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    parent_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    
    __table_args__ = (
        Index("ix_industries_level", "level"),
    )

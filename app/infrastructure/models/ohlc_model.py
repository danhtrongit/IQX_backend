"""Stock OHLC Daily ORM model."""
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import BigInteger, String, Date, DateTime, Numeric, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.base import Base


class StockOHLCDailyModel(Base):
    """Stock OHLC Daily database model for caching historical price data."""

    __tablename__ = "stock_ohlc_daily"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)
    open: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    high: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    low: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    close: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    # Moving Average columns for price
    ma5: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    ma10: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    ma20: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    ma30: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    ma50: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    ma100: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    ma200: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)

    # Moving Average columns for volume
    vol_ma5: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    vol_ma10: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    vol_ma20: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    vol_ma30: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    vol_ma50: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    vol_ma100: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    vol_ma200: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    __table_args__ = (
        Index("uk_ohlc_symbol_date", "symbol", "trade_date", unique=True),
        Index("ix_ohlc_symbol", "symbol"),
        Index("ix_ohlc_trade_date", "trade_date"),
        Index("ix_ohlc_symbol_date_range", "symbol", "trade_date"),
    )

    def __repr__(self) -> str:
        return f"<StockOHLCDaily {self.symbol} {self.trade_date}>"

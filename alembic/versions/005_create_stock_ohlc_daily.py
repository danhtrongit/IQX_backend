"""Create stock_ohlc_daily table for caching OHLC data

Revision ID: 005
Revises: 004
Create Date: 2025-01-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'stock_ohlc_daily',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('symbol', sa.String(20), nullable=False),
        sa.Column('trade_date', sa.Date(), nullable=False),
        sa.Column('open', sa.Numeric(12, 2), nullable=False),
        sa.Column('high', sa.Numeric(12, 2), nullable=False),
        sa.Column('low', sa.Numeric(12, 2), nullable=False),
        sa.Column('close', sa.Numeric(12, 2), nullable=False),
        sa.Column('volume', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),

        sa.PrimaryKeyConstraint('id'),
    )

    # Unique constraint on symbol + trade_date
    op.create_index('uk_ohlc_symbol_date', 'stock_ohlc_daily', ['symbol', 'trade_date'], unique=True)

    # Indexes for common queries
    op.create_index('ix_ohlc_symbol', 'stock_ohlc_daily', ['symbol'])
    op.create_index('ix_ohlc_trade_date', 'stock_ohlc_daily', ['trade_date'])

    # Composite index for range queries (screener use case)
    op.create_index('ix_ohlc_symbol_date_range', 'stock_ohlc_daily', ['symbol', 'trade_date'])


def downgrade() -> None:
    op.drop_table('stock_ohlc_daily')

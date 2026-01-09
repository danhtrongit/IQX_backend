"""Add MA columns to stock_ohlc_daily table

Revision ID: 006
Revises: 005
Create Date: 2026-01-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add MA columns for price
    op.add_column('stock_ohlc_daily', sa.Column('ma5', sa.Numeric(12, 2), nullable=True))
    op.add_column('stock_ohlc_daily', sa.Column('ma10', sa.Numeric(12, 2), nullable=True))
    op.add_column('stock_ohlc_daily', sa.Column('ma20', sa.Numeric(12, 2), nullable=True))
    op.add_column('stock_ohlc_daily', sa.Column('ma30', sa.Numeric(12, 2), nullable=True))
    op.add_column('stock_ohlc_daily', sa.Column('ma50', sa.Numeric(12, 2), nullable=True))
    op.add_column('stock_ohlc_daily', sa.Column('ma100', sa.Numeric(12, 2), nullable=True))
    op.add_column('stock_ohlc_daily', sa.Column('ma200', sa.Numeric(12, 2), nullable=True))

    # Add MA columns for volume
    op.add_column('stock_ohlc_daily', sa.Column('vol_ma5', sa.BigInteger(), nullable=True))
    op.add_column('stock_ohlc_daily', sa.Column('vol_ma10', sa.BigInteger(), nullable=True))
    op.add_column('stock_ohlc_daily', sa.Column('vol_ma20', sa.BigInteger(), nullable=True))
    op.add_column('stock_ohlc_daily', sa.Column('vol_ma30', sa.BigInteger(), nullable=True))
    op.add_column('stock_ohlc_daily', sa.Column('vol_ma50', sa.BigInteger(), nullable=True))
    op.add_column('stock_ohlc_daily', sa.Column('vol_ma100', sa.BigInteger(), nullable=True))
    op.add_column('stock_ohlc_daily', sa.Column('vol_ma200', sa.BigInteger(), nullable=True))


def downgrade() -> None:
    # Remove volume MA columns
    op.drop_column('stock_ohlc_daily', 'vol_ma200')
    op.drop_column('stock_ohlc_daily', 'vol_ma100')
    op.drop_column('stock_ohlc_daily', 'vol_ma50')
    op.drop_column('stock_ohlc_daily', 'vol_ma30')
    op.drop_column('stock_ohlc_daily', 'vol_ma20')
    op.drop_column('stock_ohlc_daily', 'vol_ma10')
    op.drop_column('stock_ohlc_daily', 'vol_ma5')

    # Remove price MA columns
    op.drop_column('stock_ohlc_daily', 'ma200')
    op.drop_column('stock_ohlc_daily', 'ma100')
    op.drop_column('stock_ohlc_daily', 'ma50')
    op.drop_column('stock_ohlc_daily', 'ma30')
    op.drop_column('stock_ohlc_daily', 'ma20')
    op.drop_column('stock_ohlc_daily', 'ma10')
    op.drop_column('stock_ohlc_daily', 'ma5')

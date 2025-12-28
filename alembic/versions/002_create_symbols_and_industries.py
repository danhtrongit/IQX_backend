"""Create symbols and industries tables

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create symbols table
    op.create_table(
        'symbols',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('symbol', sa.String(20), nullable=False),
        sa.Column('organ_name', sa.String(255), nullable=True),
        sa.Column('en_organ_name', sa.String(255), nullable=True),
        sa.Column('organ_short_name', sa.String(100), nullable=True),
        sa.Column('exchange', sa.String(20), nullable=True),
        sa.Column('type', sa.String(20), nullable=True),
        
        # ICB Industry Classification
        sa.Column('icb_code1', sa.String(10), nullable=True),
        sa.Column('icb_code2', sa.String(10), nullable=True),
        sa.Column('icb_code3', sa.String(10), nullable=True),
        sa.Column('icb_code4', sa.String(10), nullable=True),
        sa.Column('icb_name2', sa.String(100), nullable=True),
        sa.Column('icb_name3', sa.String(100), nullable=True),
        sa.Column('icb_name4', sa.String(100), nullable=True),
        
        # Company details
        sa.Column('company_profile', sa.Text(), nullable=True),
        sa.Column('history', sa.Text(), nullable=True),
        sa.Column('issue_share', sa.Numeric(20, 2), nullable=True),
        sa.Column('charter_capital', sa.Numeric(20, 2), nullable=True),
        
        # Metadata
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create indexes for symbols
    op.create_index('ix_symbols_symbol', 'symbols', ['symbol'], unique=True)
    op.create_index('ix_symbols_exchange', 'symbols', ['exchange'])
    op.create_index('ix_symbols_type', 'symbols', ['type'])
    op.create_index('ix_symbols_icb_code2', 'symbols', ['icb_code2'])
    op.create_index('ix_symbols_is_active', 'symbols', ['is_active'])
    
    # Create industries table
    op.create_table(
        'industries',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('icb_code', sa.String(10), nullable=False),
        sa.Column('icb_name', sa.String(100), nullable=False),
        sa.Column('en_icb_name', sa.String(100), nullable=True),
        sa.Column('level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('parent_code', sa.String(10), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create indexes for industries
    op.create_index('ix_industries_icb_code', 'industries', ['icb_code'], unique=True)
    op.create_index('ix_industries_level', 'industries', ['level'])


def downgrade() -> None:
    op.drop_table('industries')
    op.drop_table('symbols')

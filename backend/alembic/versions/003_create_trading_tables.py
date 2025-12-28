"""Create trading tables.

Revision ID: 003
Revises: 002
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Wallets table
    op.create_table(
        "wallets",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("balance", sa.Numeric(20, 2), nullable=False, server_default="0"),
        sa.Column("locked", sa.Numeric(20, 2), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(10), nullable=False, server_default="VND"),
        sa.Column("first_grant_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_wallets_user_id", "wallets", ["user_id"], unique=True)
    
    # Positions table
    op.create_table(
        "positions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("symbol", sa.String(20), nullable=False),
        sa.Column("quantity", sa.Numeric(20, 4), nullable=False, server_default="0"),
        sa.Column("locked_quantity", sa.Numeric(20, 4), nullable=False, server_default="0"),
        sa.Column("avg_price", sa.Numeric(20, 4), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_positions_user_symbol", "positions", ["user_id", "symbol"], unique=True)
    
    # Orders table
    op.create_table(
        "orders",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("symbol", sa.String(20), nullable=False),
        sa.Column("side", sa.String(4), nullable=False),
        sa.Column("type", sa.String(10), nullable=False),
        sa.Column("quantity", sa.Numeric(20, 4), nullable=False),
        sa.Column("limit_price", sa.Numeric(20, 4), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="NEW"),
        sa.Column("filled_quantity", sa.Numeric(20, 4), nullable=False, server_default="0"),
        sa.Column("avg_filled_price", sa.Numeric(20, 4), nullable=False, server_default="0"),
        sa.Column("fee_total", sa.Numeric(20, 4), nullable=False, server_default="0"),
        sa.Column("price_snapshot", sa.Numeric(20, 4), nullable=True),
        sa.Column("client_order_id", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("canceled_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_orders_user_id", "orders", ["user_id"])
    op.create_index("ix_orders_status", "orders", ["status"])
    op.create_index("ix_orders_symbol", "orders", ["symbol"])
    op.create_index("ix_orders_created_at", "orders", ["created_at"])
    op.create_index("ix_orders_client_order_id", "orders", ["user_id", "client_order_id"], unique=True)
    
    # Trades table
    op.create_table(
        "trades",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("order_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("symbol", sa.String(20), nullable=False),
        sa.Column("side", sa.String(4), nullable=False),
        sa.Column("quantity", sa.Numeric(20, 4), nullable=False),
        sa.Column("price", sa.Numeric(20, 4), nullable=False),
        sa.Column("fee", sa.Numeric(20, 4), nullable=False, server_default="0"),
        sa.Column("executed_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_trades_order_id", "trades", ["order_id"])
    op.create_index("ix_trades_user_id", "trades", ["user_id"])
    op.create_index("ix_trades_executed_at", "trades", ["executed_at"])
    
    # Ledger entries table
    op.create_table(
        "ledger_entries",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("entry_type", sa.String(30), nullable=False),
        sa.Column("amount", sa.Numeric(20, 2), nullable=False),
        sa.Column("balance_after", sa.Numeric(20, 2), nullable=False),
        sa.Column("ref_type", sa.String(30), nullable=True),
        sa.Column("ref_id", sa.BigInteger(), nullable=True),
        sa.Column("meta_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_ledger_entries_user_id", "ledger_entries", ["user_id"])
    op.create_index("ix_ledger_entries_created_at", "ledger_entries", ["created_at"])
    op.create_index("ix_ledger_entries_entry_type", "ledger_entries", ["entry_type"])


def downgrade() -> None:
    op.drop_table("ledger_entries")
    op.drop_table("trades")
    op.drop_table("orders")
    op.drop_table("positions")
    op.drop_table("wallets")

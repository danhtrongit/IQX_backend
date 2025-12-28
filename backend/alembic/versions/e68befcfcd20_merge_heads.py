"""merge_heads

Revision ID: e68befcfcd20
Revises: 003, 1466d759c706
Create Date: 2025-12-19 09:45:19.189342

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e68befcfcd20'
down_revision: Union[str, None] = ('003', '1466d759c706')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

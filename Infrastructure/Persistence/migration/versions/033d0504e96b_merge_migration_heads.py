"""merge migration heads

Revision ID: 033d0504e96b
Revises: 05afef6326d9, bd76aac81ee4
Create Date: 2026-09-18 11:53:59.838034

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '033d0504e96b'
down_revision: Union[str, Sequence[str], None] = ('05afef6326d9', 'bd76aac81ee4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

"""merge multiple heads

Revision ID: 4075f1c8f9b3
Revises: 033d0504e96b, 83c9a4e21b7f
Create Date: 2026-09-19 20:13:55.372406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4075f1c8f9b3'
down_revision: Union[str, Sequence[str], None] = ('033d0504e96b', '83c9a4e21b7f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

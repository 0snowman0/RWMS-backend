"""add_status_column_to_waybills

Revision ID: cbe15d757a58
Revises: 4075f1c8f9b3
Create Date: 2026-09-24 22:22:12.347238

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cbe15d757a58'
down_revision: Union[str, Sequence[str], None] = '4075f1c8f9b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Ensure columns match domain model
    op.execute("ALTER TABLE waybills ADD COLUMN IF NOT EXISTS name VARCHAR(255) NOT NULL DEFAULT ''")
    op.execute("ALTER TABLE waybills ADD COLUMN IF NOT EXISTS attributes JSONB NOT NULL DEFAULT '[]'::jsonb")
    op.execute("ALTER TABLE waybills ADD COLUMN IF NOT EXISTS status VARCHAR(30) NOT NULL DEFAULT 'registered'")

    # Relax columns that are optional in domain model
    op.execute("ALTER TABLE waybills ALTER COLUMN waybill_number DROP NOT NULL")
    op.execute("ALTER TABLE waybills ALTER COLUMN waybill_date DROP NOT NULL")
    op.execute("ALTER TABLE waybills ALTER COLUMN sender_name DROP NOT NULL")
    op.execute("ALTER TABLE waybills ALTER COLUMN receiver_name DROP NOT NULL")
    op.execute("ALTER TABLE waybills ALTER COLUMN origin DROP NOT NULL")
    op.execute("ALTER TABLE waybills ALTER COLUMN destination DROP NOT NULL")

    # Drop deprecated columns
    op.execute("ALTER TABLE waybills DROP COLUMN IF EXISTS total_items_count")
    op.execute("ALTER TABLE waybills DROP COLUMN IF EXISTS dynamic_fields")

    # Drop deprecated table
    op.execute("DROP TABLE IF EXISTS waybillitems CASCADE")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE waybills DROP COLUMN IF EXISTS name")
    op.execute("ALTER TABLE waybills DROP COLUMN IF EXISTS attributes")
    op.execute("ALTER TABLE waybills DROP COLUMN IF EXISTS status")
    op.execute("ALTER TABLE waybills ADD COLUMN IF NOT EXISTS total_items_count INTEGER")
    op.execute("ALTER TABLE waybills ADD COLUMN IF NOT EXISTS dynamic_fields JSONB NOT NULL DEFAULT '{}'::jsonb")

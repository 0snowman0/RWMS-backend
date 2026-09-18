"""create waybills and waybill items tables

Revision ID: 83c9a4e21b7f
Revises: 05afef6326d9
Create Date: 2026-09-18 16:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '83c9a4e21b7f'
down_revision: Union[str, Sequence[str], None] = '033d0504e96b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'waybills',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('waybill_number', sa.String(length=100), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=False),
        sa.Column('waybill_date', sa.Date(), nullable=False),
        sa.Column('received_date', sa.Date(), nullable=True),
        sa.Column('sender_name', sa.String(length=255), nullable=False),
        sa.Column('sender_contact', sa.String(length=255), nullable=True),
        sa.Column('receiver_name', sa.String(length=255), nullable=False),
        sa.Column('receiver_contact', sa.String(length=255), nullable=True),
        sa.Column('origin', sa.String(length=255), nullable=False),
        sa.Column('destination', sa.String(length=255), nullable=False),
        sa.Column('vehicle_type', sa.String(length=100), nullable=True),
        sa.Column('vehicle_number', sa.String(length=50), nullable=True),
        sa.Column('driver_name', sa.String(length=255), nullable=True),
        sa.Column('driver_contact', sa.String(length=50), nullable=True),
        sa.Column('total_items_count', sa.Integer(), nullable=True),
        sa.Column('total_weight', sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='registered'),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='normal'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('internal_notes', sa.Text(), nullable=True),
        sa.Column('dynamic_fields', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['template_id'], ['waybilltemplates.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('waybill_number')
    )

    op.create_table(
        'waybillitems',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('waybill_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=True),
        sa.Column('item_name', sa.String(length=255), nullable=False),
        sa.Column('quantity_sent', sa.Integer(), nullable=False),
        sa.Column('quantity_received', sa.Integer(), nullable=True),
        sa.Column('batch_number', sa.String(length=100), nullable=True),
        sa.Column('manufacturing_date', sa.Date(), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('quality_status', sa.String(length=20), nullable=False, server_default='good'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['waybill_id'], ['waybills.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('waybillitems')
    op.drop_table('waybills')

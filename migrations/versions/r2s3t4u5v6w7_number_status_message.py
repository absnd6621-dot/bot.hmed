"""Persist number purchase intent and reconciliation messages.

Revision ID: r2s3t4u5v6w7
Revises: q1r2s3t4u5v6
"""
from alembic import op
import sqlalchemy as sa

revision = "r2s3t4u5v6w7"
down_revision = "q1r2s3t4u5v6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("number_orders", sa.Column("status_message", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("number_orders", "status_message")

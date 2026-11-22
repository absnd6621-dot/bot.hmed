"""Add the ORM's UNKNOWN order status to the actual PostgreSQL enum.

Revision ID: q1r2s3t4u5v6
Revises: p0q1r2s3t4u5

The older migration attempted to add lowercase 'unknown' on a separate
connection, which cannot see a newly-created uncommitted enum. SQLAlchemy's
Enum(OrderStatus) stores member names, so the required label is 'UNKNOWN'.
This migration repairs both new and already-migrated databases without touching
existing orders. The new value is not used until the migration commits.
"""
from alembic import op

revision = "q1r2s3t4u5v6"
down_revision = "p0q1r2s3t4u5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
    op.execute("""
        DO $$
        DECLARE enum_schema text; enum_name text;
        BEGIN
            SELECT n.nspname, t.typname INTO enum_schema, enum_name
            FROM pg_attribute a
            JOIN pg_type t ON t.oid = a.atttypid
            JOIN pg_namespace n ON n.oid = t.typnamespace
            WHERE a.attrelid = 'number_orders'::regclass
              AND a.attname = 'status' AND NOT a.attisdropped
              AND t.typtype = 'e';
            IF enum_name IS NULL THEN
                RAISE EXCEPTION 'number_orders.status is not a PostgreSQL enum';
            END IF;
            EXECUTE format('ALTER TYPE %I.%I ADD VALUE IF NOT EXISTS %L',
                           enum_schema, enum_name, 'UNKNOWN');
        END $$;
    """)


def downgrade() -> None:
    # PostgreSQL cannot safely remove enum labels in place; retain existing data.
    pass

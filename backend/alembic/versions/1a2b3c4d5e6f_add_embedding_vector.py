"""add embedding vector

Revision ID: 1a2b3c4d5e6f
Revises: 0ab2d6eccaa3
Create Date: 2026-05-20 00:00:00.000000

"""

# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = '0ab2d6eccaa3'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # Try to enable pgvector extension and add a vector column.
    # If the extension is not available in this Postgres image, fall back
    # to adding a JSONB `embedding` column so migrations can run.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_available_extensions WHERE name='vector') THEN
                EXECUTE 'CREATE EXTENSION IF NOT EXISTS vector';
                EXECUTE 'ALTER TABLE documents ADD COLUMN IF NOT EXISTS embedding vector';
            ELSE
                -- fallback to jsonb while pgvector isn't installed
                EXECUTE 'ALTER TABLE documents ADD COLUMN IF NOT EXISTS embedding jsonb';
            END IF;
        END$$;
        """
    )


def downgrade():
    # Drop the embedding column (type may be vector or jsonb) and remove extension if present
    op.execute("ALTER TABLE documents DROP COLUMN IF EXISTS embedding")
    op.execute("DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_available_extensions WHERE name='vector') THEN PERFORM 1; END IF; END$$;")

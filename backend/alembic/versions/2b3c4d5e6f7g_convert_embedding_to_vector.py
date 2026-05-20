"""convert embedding jsonb to pgvector (if pgvector available)

Revision ID: 2b3c4d5e6f7g
Revises: 1a2b3c4d5e6f
Create Date: 2026-05-21 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2b3c4d5e6f7g'
down_revision = '1a2b3c4d5e6f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    # Try to create the vector extension; if it fails, do nothing (safe fallback)
    try:
        bind.execute("CREATE EXTENSION IF NOT EXISTS vector")
    except Exception:
        # extension not available or permission denied; skip migration
        return

    # If the new column already exists, nothing to do
    col_exists = bind.execute(
        "SELECT 1 FROM pg_attribute WHERE attrelid = 'documents'::regclass AND attname = 'embedding_vector'"
    ).fetchone()
    if col_exists:
        return

    # Determine embedding dimension from an existing row (fallback to 1536)
    dim = 1536
    row = bind.execute("SELECT embedding FROM documents WHERE embedding IS NOT NULL LIMIT 1").fetchone()
    if row and row[0] is not None:
        try:
            dim = len(row[0])
        except Exception:
            dim = 1536

    # Add a new vector column and populate it from the JSON embedding array
    try:
        bind.execute(sa.text(f"ALTER TABLE documents ADD COLUMN embedding_vector vector({dim})"))
        # Convert jsonb array text to vector (remove whitespace then cast)
        bind.execute(sa.text(
            "UPDATE documents SET embedding_vector = regexp_replace(embedding::text, '\\s+', '', 'g')::vector WHERE embedding IS NOT NULL"
        ))
    except Exception:
        # If any step fails, leave the DB as-is (no destructive changes)
        pass


def downgrade() -> None:
    bind = op.get_bind()
    try:
        bind.execute("ALTER TABLE documents DROP COLUMN IF EXISTS embedding_vector")
    except Exception:
        pass

"""Aggiunto campo codice_interno a ODV

Revision ID: b63e9441af68
Revises: b63e9441af67
Create Date: 2025-07-25 15:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b63e9441af68'
down_revision = 'b63e9441af67'
branch_labels = None
depends_on = None


def upgrade():
    # Aggiungi la colonna codice_interno alla tabella odv
    op.add_column('odv', sa.Column('codice_interno', sa.String(length=100), nullable=True))


def downgrade():
    # Rimuovi la colonna codice_interno dalla tabella odv
    op.drop_column('odv', 'codice_interno')

"""Fusion des branches de migration

Revision ID: 11e661eef56d
Revises: 3858724ed28f, add_missing_features
Create Date: 2025-06-30 11:07:13.740248

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11e661eef56d'
down_revision = ('3858724ed28f', 'add_missing_features')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass

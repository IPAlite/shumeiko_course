"""initial migration

Revision ID: 903cf891ec3d
Revises: 
Create Date: 2025-06-18 14:36:52.117924

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '903cf891ec3d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('hotels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('location', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )



def downgrade() -> None:
    op.drop_table('hotels')

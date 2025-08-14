from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "73edd0298988"
down_revision: Union[str, Sequence[str], None] = "cdc1de6ab293"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("bookings", sa.Column("hotel_id", sa.Integer(), nullable=False))
    op.create_foreign_key(None, "bookings", "hotels", ["hotel_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint(None, "bookings", type_="foreignkey")
    op.drop_column("bookings", "hotel_id")

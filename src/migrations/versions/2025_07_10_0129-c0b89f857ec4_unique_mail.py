from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa  # noqa


revision: str = "c0b89f857ec4"
down_revision: Union[str, Sequence[str], None] = "e4b98073aa96"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(None, "users", ["email"])


def downgrade() -> None:
    op.drop_constraint(None, "users", type_="unique")

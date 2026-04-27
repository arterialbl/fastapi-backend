"""add default to is_active

Revision ID: dab7cebcdb7a
Revises: 8fc46f8761de
Create Date: 2026-04-17 00:20:38.160351

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dab7cebcdb7a'
down_revision: Union[str, Sequence[str], None] = '8fc46f8761de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "is_active",
        server_default=sa.text("true"),
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "is_active",
        server_default=None,
    )

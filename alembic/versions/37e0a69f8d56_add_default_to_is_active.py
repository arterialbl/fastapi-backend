"""add default to is_active

Revision ID: 37e0a69f8d56
Revises: 11dfc43bf180
Create Date: 2026-04-17 00:23:26.294923

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '37e0a69f8d56'
down_revision: Union[str, Sequence[str], None] = '11dfc43bf180'
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
"""Add CheckConstraint on Event.name_id

Revision ID: d17fa3f5c60a
Revises: 74126203a837
Create Date: 2025-05-08 19:26:21.111855

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd17fa3f5c60a'
down_revision: Union[str, None] = '74126203a837'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        constraint_name='valid_named_id',
        table_name='events',
        condition="char_length(named_id) <= 32 AND named_id ~ '^[a-zA-Z0-9-]+$'"
    )
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        constraint_name='valid_named_id',
        table_name='events',
        type_='check'
    )
    pass
    # ### end Alembic commands ###

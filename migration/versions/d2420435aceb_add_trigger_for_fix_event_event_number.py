"""Add trigger for fix Event.event_number

Revision ID: d2420435aceb
Revises: d17fa3f5c60a
Create Date: 2025-05-08 20:10:14.147292

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from database.models.triggers import fix_event_number_on_insert_trigger

# revision identifiers, used by Alembic.
revision: str = 'd2420435aceb'
down_revision: Union[str, None] = 'd17fa3f5c60a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for command in fix_event_number_on_insert_trigger['upgrade']:
        op.execute(command)


def downgrade() -> None:
    for command in fix_event_number_on_insert_trigger['downgrade']:
        op.execute(command)

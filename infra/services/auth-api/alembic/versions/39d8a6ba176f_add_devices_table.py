"""add devices table

Revision ID: 39d8a6ba176f
Revises: 3929a63c9eae
Create Date: 2025-05-27 17:58:13.696187

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39d8a6ba176f'
down_revision: Union[str, None] = '3929a63c9eae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

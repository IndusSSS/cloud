"""add devices table"""

from alembic import op
import sqlalchemy as sa

# TODO: set this to the ID of the migration immediately before this one
revision = "3929a63c9eae"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "devices",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id")),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("status", sa.String(16), server_default="offline"),
    )

def downgrade():
    op.drop_table("devices")

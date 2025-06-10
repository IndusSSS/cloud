"""add devices table"""

from alembic import op
import sqlalchemy as sa

# this migration builds on the metrics table revision
revision = "39d8a6ba176f"
down_revision = "3929a63c9eae"
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

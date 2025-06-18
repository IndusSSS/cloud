from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'tenant',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('plan', sa.String, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('tenant_id', sa.Integer, sa.ForeignKey('tenant.id')),
        sa.Column('email', sa.String, nullable=False, unique=True),
        sa.Column('password_hash', sa.String, nullable=False),
        sa.Column('role', sa.String, nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )
    op.create_table(
        'device',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('tenant_id', sa.Integer, sa.ForeignKey('tenant.id')),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('type', sa.String, nullable=False),
        sa.Column('last_seen', sa.DateTime),
        sa.Column('status', sa.String),
    )
    op.create_table(
        'metric',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('device_id', sa.Integer, sa.ForeignKey('device.id')),
        sa.Column('ts', sa.DateTime, nullable=False),
        sa.Column('key', sa.String, nullable=False),
        sa.Column('value', sa.Float, nullable=False),
    )
    op.create_table(
        'refreshtoken',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id')),
        sa.Column('token', sa.String, nullable=False),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('revoked', sa.Boolean, nullable=False, server_default='0'),
    )


def downgrade() -> None:
    op.drop_table('refreshtoken')
    op.drop_table('metric')
    op.drop_table('device')
    op.drop_table('user')
    op.drop_table('tenant')

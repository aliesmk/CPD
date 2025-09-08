from alembic import op
import sqlalchemy as sa

revision = 'aaaa'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'crypto_prices',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('coin_id', sa.String, nullable=False),
        sa.Column('open', sa.Float, nullable=False),
        sa.Column('high', sa.Float, nullable=False),
        sa.Column('low', sa.Float, nullable=False),
        sa.Column('close', sa.Float, nullable=False),
        sa.Column('currency', sa.String, nullable=False),
        sa.Column('timestamp', sa.DateTime, nullable=False),
        sa.Column('candle_type', sa.String, nullable=False),
        sa.UniqueConstraint('coin_id', 'timestamp', name='uix_coin_timestamp')
    )

def downgrade():
    op.drop_table('crypto_prices')
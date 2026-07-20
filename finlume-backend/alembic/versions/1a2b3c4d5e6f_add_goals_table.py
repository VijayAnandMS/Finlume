"""Add goals table

Revision ID: 1a2b3c4d5e6f
Revises: fef0ac630fc5
Create Date: 2026-07-20 19:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = 'fef0ac630fc5'
branch_labels = None
depends_on = None

def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    if 'goals' not in inspector.get_table_names():
        op.create_table('goals',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('target_amount', sa.Float(), nullable=False),
            sa.Column('current_amount', sa.Float(), nullable=True, default=0.0),
            sa.Column('deadline', sa.String(), nullable=True),
            sa.Column('status', sa.String(), nullable=True, default='active'),
            sa.Column('monthly_target', sa.Float(), nullable=True),
            sa.Column('priority', sa.String(), nullable=True, default='medium'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_goals_id'), 'goals', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_goals_id'), table_name='goals')
    op.drop_table('goals')

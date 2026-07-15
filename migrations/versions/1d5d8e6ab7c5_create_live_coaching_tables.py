"""create_live_coaching_tables

Revision ID: 1d5d8e6ab7c5
Revises: ef137c768ceb
Create Date: 2026-07-14 19:35:49.594881

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d5d8e6ab7c5'
down_revision: Union[str, None] = 'ef137c768ceb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. create live_sessions
    op.create_table(
        'live_sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_live_sessions_id'), 'live_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_live_sessions_user_id'), 'live_sessions', ['user_id'], unique=False)

    # 2. create session_states
    op.create_table(
        'session_states',
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('round_number', sa.Integer(), nullable=False),
        sa.Column('kills', sa.Integer(), nullable=False),
        sa.Column('deaths', sa.Integer(), nullable=False),
        sa.Column('assists', sa.Integer(), nullable=False),
        sa.Column('credits', sa.Integer(), nullable=False),
        sa.Column('fatigue_index', sa.Float(), nullable=False),
        sa.Column('tilt_score', sa.Float(), nullable=False),
        sa.Column('win_probability', sa.Float(), nullable=False),
        sa.Column('recommendations', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['live_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('session_id', 'round_number')
    )

    # 3. create goal_tracking
    op.create_table(
        'goal_tracking',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('target_metric', sa.String(length=50), nullable=False),
        sa.Column('target_value', sa.Float(), nullable=False),
        sa.Column('current_value', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_goal_tracking_id'), 'goal_tracking', ['id'], unique=False)
    op.create_index(op.f('ix_goal_tracking_user_id'), 'goal_tracking', ['user_id'], unique=False)

    # 4. create training_plans
    op.create_table(
        'training_plans',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('daily_drills', sa.JSON(), nullable=False),
        sa.Column('weekly_drills', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_training_plans_id'), 'training_plans', ['id'], unique=False)
    op.create_index(op.f('ix_training_plans_user_id'), 'training_plans', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_training_plans_user_id'), table_name='training_plans')
    op.drop_index(op.f('ix_training_plans_id'), table_name='training_plans')
    op.drop_table('training_plans')
    op.drop_index(op.f('ix_goal_tracking_user_id'), table_name='goal_tracking')
    op.drop_index(op.f('ix_goal_tracking_id'), table_name='goal_tracking')
    op.drop_table('goal_tracking')
    op.drop_table('session_states')
    op.drop_index(op.f('ix_live_sessions_user_id'), table_name='live_sessions')
    op.drop_index(op.f('ix_live_sessions_id'), table_name='live_sessions')
    op.drop_table('live_sessions')

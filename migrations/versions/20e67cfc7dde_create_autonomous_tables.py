"""create_autonomous_tables

Revision ID: 20e67cfc7dde
Revises: 1d5d8e6ab7c5
Create Date: 2026-07-14 20:11:43.749539

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20e67cfc7dde'
down_revision: Union[str, None] = '1d5d8e6ab7c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. create player_memory
    op.create_table(
        'player_memory',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('memory_type', sa.String(length=20), nullable=False),
        sa.Column('insight', sa.String(length=1000), nullable=False),
        sa.Column('importance_score', sa.Float(), nullable=False),
        sa.Column('decay_rate', sa.Float(), nullable=False),
        sa.Column('embedding', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_player_memory_id'), 'player_memory', ['id'], unique=False)
    op.create_index(op.f('ix_player_memory_user_id'), 'player_memory', ['user_id'], unique=False)

    # 2. create player_dna
    op.create_table(
        'player_dna',
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('aim_consistency', sa.Float(), nullable=False),
        sa.Column('aggression_index', sa.Float(), nullable=False),
        sa.Column('economy_discipline', sa.Float(), nullable=False),
        sa.Column('patience_rating', sa.Float(), nullable=False),
        sa.Column('tilt_resistance', sa.Float(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_player_dna_user_id'), 'player_dna', ['user_id'], unique=False)

    # 3. create digital_twins
    op.create_table(
        'digital_twins',
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('simulation_parameters', sa.JSON(), nullable=False),
        sa.Column('accuracy_score', sa.Float(), nullable=False),
        sa.Column('last_calibrated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_digital_twins_user_id'), 'digital_twins', ['user_id'], unique=False)

    # 4. create learning_history
    op.create_table(
        'learning_history',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('skill_category', sa.String(length=50), nullable=False),
        sa.Column('metric_delta', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learning_history_id'), 'learning_history', ['id'], unique=False)
    op.create_index(op.f('ix_learning_history_user_id'), 'learning_history', ['user_id'], unique=False)

    # 5. create recommendation_feedback
    op.create_table(
        'recommendation_feedback',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('drill_id', sa.String(length=50), nullable=False),
        sa.Column('was_helpful', sa.Boolean(), nullable=False),
        sa.Column('satisfaction_score', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recommendation_feedback_id'), 'recommendation_feedback', ['id'], unique=False)
    op.create_index(op.f('ix_recommendation_feedback_user_id'), 'recommendation_feedback', ['user_id'], unique=False)

    # 6. create coaching_sessions
    op.create_table(
        'coaching_sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('coach_persona', sa.String(length=50), nullable=False),
        sa.Column('feedback_notes', sa.String(length=2000), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_coaching_sessions_id'), 'coaching_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_coaching_sessions_user_id'), 'coaching_sessions', ['user_id'], unique=False)

    # 7. create seasonal_progress
    op.create_table(
        'seasonal_progress',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('season_id', sa.String(length=20), nullable=False),
        sa.Column('start_rr', sa.Integer(), nullable=False),
        sa.Column('end_rr', sa.Integer(), nullable=False),
        sa.Column('win_count', sa.Integer(), nullable=False),
        sa.Column('loss_count', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_seasonal_progress_id'), 'seasonal_progress', ['id'], unique=False)
    op.create_index(op.f('ix_seasonal_progress_user_id'), 'seasonal_progress', ['user_id'], unique=False)

    # 8. create curriculum_plans
    op.create_table(
        'curriculum_plans',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('plan_duration_days', sa.Integer(), nullable=False),
        sa.Column('drills_sequence', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_curriculum_plans_id'), 'curriculum_plans', ['id'], unique=False)
    op.create_index(op.f('ix_curriculum_plans_user_id'), 'curriculum_plans', ['user_id'], unique=False)

    # 9. create ai_plans
    op.create_table(
        'ai_plans',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('target_milestone', sa.String(length=100), nullable=False),
        sa.Column('action_steps', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_plans_id'), 'ai_plans', ['id'], unique=False)
    op.create_index(op.f('ix_ai_plans_user_id'), 'ai_plans', ['user_id'], unique=False)

    # 10. create simulation_results
    op.create_table(
        'simulation_results',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('simulation_type', sa.String(length=50), nullable=False),
        sa.Column('raw_parameters', sa.JSON(), nullable=False),
        sa.Column('victory_probability', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_simulation_results_id'), 'simulation_results', ['id'], unique=False)
    op.create_index(op.f('ix_simulation_results_user_id'), 'simulation_results', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_table('simulation_results')
    op.drop_table('ai_plans')
    op.drop_table('curriculum_plans')
    op.drop_table('seasonal_progress')
    op.drop_table('coaching_sessions')
    op.drop_table('recommendation_feedback')
    op.drop_table('learning_history')
    op.drop_table('digital_twins')
    op.drop_table('player_dna')
    op.drop_table('player_memory')

"""create_federation_tables

Revision ID: 0c47e1c53db5
Revises: 20e67cfc7dde
Create Date: 2026-07-14 20:17:39.619185

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c47e1c53db5'
down_revision: Union[str, None] = '20e67cfc7dde'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. create federated_rounds
    op.create_table(
        'federated_rounds',
        sa.Column('round_number', sa.Integer(), nullable=False),
        sa.Column('global_model_version', sa.String(length=50), nullable=False),
        sa.Column('client_participation_count', sa.Integer(), nullable=False),
        sa.Column('aggregated_weights', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('round_number')
    )

    # 2. create client_updates
    op.create_table(
        'client_updates',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('round_number', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.String(length=36), nullable=False),
        sa.Column('local_weights', sa.JSON(), nullable=False),
        sa.Column('local_loss', sa.Float(), nullable=False),
        sa.Column('client_weight', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['round_number'], ['federated_rounds.round_number'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_client_updates_id'), 'client_updates', ['id'], unique=False)
    op.create_index(op.f('ix_client_updates_client_id'), 'client_updates', ['client_id'], unique=False)

    # 3. create privacy_budgets
    op.create_table(
        'privacy_budgets',
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('epsilon_spent', sa.Float(), nullable=False),
        sa.Column('delta_spent', sa.Float(), nullable=False),
        sa.Column('max_budget_epsilon', sa.Float(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_privacy_budgets_user_id'), 'privacy_budgets', ['user_id'], unique=False)

    # 4. create benchmark_snapshots
    op.create_table(
        'benchmark_snapshots',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('rank_tier_distribution', sa.JSON(), nullable=False),
        sa.Column('agent_pick_rates', sa.JSON(), nullable=False),
        sa.Column('weapon_kill_shares', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_benchmark_snapshots_id'), 'benchmark_snapshots', ['id'], unique=False)

    # 5. create meta_reports
    op.create_table(
        'meta_reports',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('patch_version', sa.String(length=20), nullable=False),
        sa.Column('detected_meta_shifts', sa.JSON(), nullable=False),
        sa.Column('agent_popularity_ranks', sa.JSON(), nullable=False),
        sa.Column('weapon_popularity_ranks', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meta_reports_id'), 'meta_reports', ['id'], unique=False)

    # 6. create marketplace_items
    op.create_table(
        'marketplace_items',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('author_id', sa.String(length=36), nullable=False),
        sa.Column('item_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('rating', sa.Float(), nullable=False),
        sa.Column('downloads_count', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_marketplace_items_id'), 'marketplace_items', ['id'], unique=False)

    # 7. create scheduler_jobs
    op.create_table(
        'scheduler_jobs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('retry_policy', sa.JSON(), nullable=False),
        sa.Column('cron_expression', sa.String(length=50), nullable=True),
        sa.Column('next_run_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scheduler_jobs_id'), 'scheduler_jobs', ['id'], unique=False)

    # 8. create governance_logs
    op.create_table(
        'governance_logs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('prompt_version', sa.String(length=50), nullable=False),
        sa.Column('prediction_hash', sa.String(length=64), nullable=False),
        sa.Column('decision_lineage', sa.JSON(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('compliance_passed', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_governance_logs_id'), 'governance_logs', ['id'], unique=False)


def downgrade() -> None:
    op.drop_table('governance_logs')
    op.drop_table('scheduler_jobs')
    op.drop_table('marketplace_items')
    op.drop_table('meta_reports')
    op.drop_table('benchmark_snapshots')
    op.drop_table('privacy_budgets')
    op.drop_table('client_updates')
    op.drop_table('federated_rounds')

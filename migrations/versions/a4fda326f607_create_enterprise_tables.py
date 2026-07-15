"""create_enterprise_tables

Revision ID: a4fda326f607
Revises: 0c47e1c53db5
Create Date: 2026-07-14 20:20:30.470028

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4fda326f607'
down_revision: Union[str, None] = '0c47e1c53db5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. create tenants
    op.create_table(
        'tenants',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tenants_id'), 'tenants', ['id'], unique=False)

    # 2. create subscriptions
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('plan_tier', sa.String(length=20), nullable=False),
        sa.Column('credits_balance', sa.Float(), nullable=False),
        sa.Column('billing_cycle', sa.String(length=20), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscriptions_id'), 'subscriptions', ['id'], unique=False)
    op.create_index(op.f('ix_subscriptions_tenant_id'), 'subscriptions', ['tenant_id'], unique=False)

    # 3. create billing_events
    op.create_table(
        'billing_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('credits_added', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_billing_events_id'), 'billing_events', ['id'], unique=False)
    op.create_index(op.f('ix_billing_events_tenant_id'), 'billing_events', ['tenant_id'], unique=False)

    # 4. create usage_metrics
    op.create_table(
        'usage_metrics',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('api_calls_count', sa.Integer(), nullable=False),
        sa.Column('websocket_connections_count', sa.Integer(), nullable=False),
        sa.Column('inference_duration_seconds', sa.Float(), nullable=False),
        sa.Column('cost_credits', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_usage_metrics_id'), 'usage_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_usage_metrics_tenant_id'), 'usage_metrics', ['tenant_id'], unique=False)

    # 5. create workflow_definitions
    op.create_table(
        'workflow_definitions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('visual_steps', sa.JSON(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflow_definitions_id'), 'workflow_definitions', ['id'], unique=False)
    op.create_index(op.f('ix_workflow_definitions_tenant_id'), 'workflow_definitions', ['tenant_id'], unique=False)

    # 6. create workflow_runs
    op.create_table(
        'workflow_runs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('workflow_id', sa.String(length=36), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('current_step', sa.Integer(), nullable=False),
        sa.Column('execution_logs', sa.JSON(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflow_definitions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflow_runs_id'), 'workflow_runs', ['id'], unique=False)
    op.create_index(op.f('ix_workflow_runs_workflow_id'), 'workflow_runs', ['workflow_id'], unique=False)

    # 7. create feature_flags
    op.create_table(
        'feature_flags',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('rollout_percentage', sa.Integer(), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_feature_flags_id'), 'feature_flags', ['id'], unique=False)

    # 8. create security_events
    op.create_table(
        'security_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('source_ip', sa.String(length=45), nullable=False),
        sa.Column('threat_score', sa.Float(), nullable=False),
        sa.Column('action_taken', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_security_events_id'), 'security_events', ['id'], unique=False)
    op.create_index(op.f('ix_security_events_tenant_id'), 'security_events', ['tenant_id'], unique=False)


def downgrade() -> None:
    op.drop_table('security_events')
    op.drop_table('feature_flags')
    op.drop_table('workflow_runs')
    op.drop_table('workflow_definitions')
    op.drop_table('usage_metrics')
    op.drop_table('billing_events')
    op.drop_table('subscriptions')
    op.drop_table('tenants')

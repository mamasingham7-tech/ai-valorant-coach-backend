"""create_coach_memories_table

Revision ID: ef137c768ceb
Revises: 41ebc6c70094
Create Date: 2026-07-14 19:29:23.287921

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef137c768ceb'
down_revision: Union[str, None] = '41ebc6c70094'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'coach_memories',
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('recurring_habits', sa.JSON(), nullable=False),
        sa.Column('resolved_habits', sa.JSON(), nullable=False),
        sa.Column('training_history', sa.JSON(), nullable=False),
        sa.Column('recommendation_history', sa.JSON(), nullable=False),
        sa.Column('player_dna', sa.JSON(), nullable=False),
        sa.Column('improvement_streaks', sa.JSON(), nullable=False),
        sa.Column('previous_sessions', sa.JSON(), nullable=False),
        sa.Column('favorite_agents', sa.JSON(), nullable=False),
        sa.Column('preferred_roles', sa.JSON(), nullable=False),
        sa.Column('goal_history', sa.JSON(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )


def downgrade() -> None:
    op.drop_table('coach_memories')

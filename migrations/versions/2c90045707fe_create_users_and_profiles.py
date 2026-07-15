"""create_users_and_profiles

Revision ID: 2c90045707fe
Revises: 
Create Date: 2026-07-14 19:11:07.492544

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c90045707fe'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create player_profiles table
    op.create_table(
        'player_profiles',
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('rank', sa.String(length=50), nullable=True),
        sa.Column('region', sa.String(length=50), nullable=True),
        sa.Column('preferred_agents', sa.JSON(), nullable=False),
        sa.Column('roles', sa.JSON(), nullable=False),
        sa.Column('sensitivity', sa.Float(), nullable=True),
        sa.Column('resolution', sa.String(length=50), nullable=True),
        sa.Column('crosshair', sa.String(length=255), nullable=True),
        sa.Column('hardware', sa.String(length=255), nullable=True),
        sa.Column('monitor_hz', sa.Integer(), nullable=True),
        sa.Column('mouse_dpi', sa.Integer(), nullable=True),
        sa.Column('playstyle', sa.String(length=100), nullable=True),
        sa.Column('preferred_maps', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )


def downgrade() -> None:
    op.drop_table('player_profiles')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')


"""create_match_and_telemetry_tables

Revision ID: 41ebc6c70094
Revises: 2c90045707fe
Create Date: 2026-07-14 19:18:46.988257

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '41ebc6c70094'
down_revision: Union[str, None] = '2c90045707fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create matches table
    op.create_table(
        'matches',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('map_name', sa.String(length=100), nullable=False),
        sa.Column('game_mode', sa.String(length=50), nullable=False),
        sa.Column('match_start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_matches_id'), 'matches', ['id'], unique=False)
    op.create_index(op.f('ix_matches_map_name'), 'matches', ['map_name'], unique=False)

    # 2. Create match_players table
    op.create_table(
        'match_players',
        sa.Column('match_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('agent_name', sa.String(length=50), nullable=False),
        sa.Column('team_id', sa.String(length=50), nullable=False),
        sa.Column('kills', sa.Integer(), nullable=False),
        sa.Column('deaths', sa.Integer(), nullable=False),
        sa.Column('assists', sa.Integer(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('damage_dealt', sa.Integer(), nullable=False),
        sa.Column('rounds_played', sa.Integer(), nullable=False),
        sa.Column('headshots', sa.Integer(), nullable=False),
        sa.Column('shots_fired', sa.Integer(), nullable=False),
        sa.Column('shots_hit', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('match_id', 'user_id')
    )
    op.create_index(op.f('ix_match_players_user_id'), 'match_players', ['user_id'], unique=False)
    op.create_index(op.f('ix_match_players_agent_name'), 'match_players', ['agent_name'], unique=False)

    # 3. Create rounds table
    op.create_table(
        'rounds',
        sa.Column('match_id', sa.String(length=36), nullable=False),
        sa.Column('round_number', sa.Integer(), nullable=False),
        sa.Column('winning_team', sa.String(length=50), nullable=False),
        sa.Column('win_reason', sa.String(length=50), nullable=False),
        sa.Column('spike_planter', sa.String(length=36), nullable=True),
        sa.Column('spike_defuser', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('match_id', 'round_number')
    )

    # 4. Create gameplay_events table with Hash partitioning on PostgreSQL, normal fallback on SQLite
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    if is_postgres:
        op.execute("""
        CREATE TABLE gameplay_events (
            id VARCHAR(36) NOT NULL,
            match_id VARCHAR(36) NOT NULL,
            round_number INTEGER NOT NULL,
            event_type VARCHAR(50) NOT NULL,
            timestamp_ms INTEGER NOT NULL,
            x_coord FLOAT,
            y_coord FLOAT,
            z_coord FLOAT,
            metadata JSON NOT NULL,
            PRIMARY KEY (id, match_id)
        ) PARTITION BY HASH (match_id);
        """)
        # Create 4 partition shards
        for i in range(4):
            op.execute(f"CREATE TABLE gameplay_events_part_{i} PARTITION OF gameplay_events FOR VALUES WITH (MODULUS 4, REMAINDER {i});")
    else:
        op.create_table(
            'gameplay_events',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('match_id', sa.String(length=36), nullable=False),
            sa.Column('round_number', sa.Integer(), nullable=False),
            sa.Column('event_type', sa.String(length=50), nullable=False),
            sa.Column('timestamp_ms', sa.Integer(), nullable=False),
            sa.Column('x_coord', sa.Float(), nullable=True),
            sa.Column('y_coord', sa.Float(), nullable=True),
            sa.Column('z_coord', sa.Float(), nullable=True),
            sa.Column('metadata', sa.JSON(), nullable=False),
            sa.PrimaryKeyConstraint('id', 'match_id')
        )
        op.create_index(op.f('ix_gameplay_events_event_type'), 'gameplay_events', ['event_type'], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    if is_postgres:
        for i in range(4):
            op.execute(f"DROP TABLE IF EXISTS gameplay_events_part_{i};")
        op.execute("DROP TABLE IF EXISTS gameplay_events;")
    else:
        op.drop_index(op.f('ix_gameplay_events_event_type'), table_name='gameplay_events')
        op.drop_table('gameplay_events')

    op.drop_table('rounds')
    op.drop_index(op.f('ix_match_players_agent_name'), table_name='match_players')
    op.drop_index(op.f('ix_match_players_user_id'), table_name='match_players')
    op.drop_table('match_players')
    op.drop_index(op.f('ix_matches_map_name'), table_name='matches')
    op.drop_index(op.f('ix_matches_id'), table_name='matches')
    op.drop_table('matches')


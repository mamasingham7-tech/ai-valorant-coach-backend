import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.core.config import settings
from app.database.database import Base
from app.modules.users.infrastructure.models.user_table import UserTable
from app.modules.users.infrastructure.models.profile_table import ProfileTable
from app.modules.users.infrastructure.models.session_table import SessionTable
from app.modules.matches.infrastructure.models.match import MatchTable
from app.modules.matches.infrastructure.models.player_stats import MatchPlayerTable
from app.modules.matches.infrastructure.models.round import RoundTable
from app.modules.matches.infrastructure.models.event import GameplayEventTable
from app.modules.ai.infrastructure.memory.models import CoachMemoryTable
from app.modules.live_coaching.infrastructure.models.live_tables import LiveSessionTable, SessionStateTable, PlayerGoalTable, TrainingPlanTable
from app.modules.autonomous.infrastructure.models.autonomous_tables import (
    PlayerMemoryTable, PlayerDNATable, DigitalTwinTable, LearningHistoryTable,
    RecommendationFeedbackTable, CoachingSessionTable, SeasonalProgressTable,
    CurriculumPlanTable, AIPlanTable, SimulationResultTable
)
from app.modules.federation.infrastructure.models.federated_models import (
    AggregationRoundTable, ClientUpdateTable, PrivacyBudgetTable, BenchmarkSnapshotTable,
    MetaReportTable, MarketplaceItemTable, SchedulerJobTable, GovernanceLogTable
)
from app.modules.enterprise.infrastructure.models.enterprise_tables import (
    TenantTable, SubscriptionTable, BillingEventTable, UsageMetricTable,
    WorkflowDefinitionTable, WorkflowRunTable, FeatureFlagTable, SecurityEventTable
)

target_metadata = Base.metadata
if settings.USE_SQLITE:
    config.set_main_option("sqlalchemy.url", "sqlite+aiosqlite:///./dev.db")
else:
    config.set_main_option("sqlalchemy.url", settings.async_database_url)


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

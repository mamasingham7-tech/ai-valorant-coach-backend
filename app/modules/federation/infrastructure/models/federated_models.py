from sqlalchemy import String, Integer, Float, JSON, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database.database import Base
from datetime import datetime

class AggregationRoundTable(Base):
    __tablename__ = "federated_rounds"

    round_number: Mapped[int] = mapped_column(Integer, primary_key=True)
    global_model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    client_participation_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    aggregated_weights: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

class ClientUpdateTable(Base):
    __tablename__ = "client_updates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    round_number: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("federated_rounds.round_number", ondelete="CASCADE"),
        nullable=False
    )
    client_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    local_weights: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    local_loss: Mapped[float] = mapped_column(Float, nullable=False)
    client_weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

class PrivacyBudgetTable(Base):
    __tablename__ = "privacy_budgets"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True
    )
    epsilon_spent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    delta_spent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    max_budget_epsilon: Mapped[float] = mapped_column(Float, default=8.0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

class BenchmarkSnapshotTable(Base):
    __tablename__ = "benchmark_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    rank_tier_distribution: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    agent_pick_rates: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    weapon_kill_shares: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

class MetaReportTable(Base):
    __tablename__ = "meta_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    patch_version: Mapped[str] = mapped_column(String(20), nullable=False)
    detected_meta_shifts: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    agent_popularity_ranks: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    weapon_popularity_ranks: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

class MarketplaceItemTable(Base):
    __tablename__ = "marketplace_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    author_id: Mapped[str] = mapped_column(String(36), nullable=False)
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)
    downloads_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PUBLISHED", nullable=False)

class SchedulerJobTable(Base):
    __tablename__ = "scheduler_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False)
    retry_policy: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    cron_expression: Mapped[str] = mapped_column(String(50), nullable=True)
    next_run_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

class GovernanceLogTable(Base):
    __tablename__ = "governance_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(50), nullable=False)
    prediction_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    decision_lineage: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    compliance_passed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

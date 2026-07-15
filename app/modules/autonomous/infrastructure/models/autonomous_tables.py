from sqlalchemy import String, Integer, Float, JSON, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database.database import Base
from datetime import datetime

class PlayerMemoryTable(Base):
    __tablename__ = "player_memory"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    memory_type: Mapped[str] = mapped_column(String(20), nullable=False)
    insight: Mapped[str] = mapped_column(String(1000), nullable=False)
    importance_score: Mapped[float] = mapped_column(Float, nullable=False)
    decay_rate: Mapped[float] = mapped_column(Float, default=0.05, nullable=False)
    embedding: Mapped[list] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

class PlayerDNATable(Base):
    __tablename__ = "player_dna"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True
    )
    aim_consistency: Mapped[float] = mapped_column(Float, nullable=False)
    aggression_index: Mapped[float] = mapped_column(Float, nullable=False)
    economy_discipline: Mapped[float] = mapped_column(Float, nullable=False)
    patience_rating: Mapped[float] = mapped_column(Float, nullable=False)
    tilt_resistance: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

class DigitalTwinTable(Base):
    __tablename__ = "digital_twins"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True
    )
    simulation_parameters: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    accuracy_score: Mapped[float] = mapped_column(Float, nullable=False)
    last_calibrated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

class LearningHistoryTable(Base):
    __tablename__ = "learning_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    skill_category: Mapped[str] = mapped_column(String(50), nullable=False)
    metric_delta: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

class RecommendationFeedbackTable(Base):
    __tablename__ = "recommendation_feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    drill_id: Mapped[str] = mapped_column(String(50), nullable=False)
    was_helpful: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    satisfaction_score: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

class CoachingSessionTable(Base):
    __tablename__ = "coaching_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    coach_persona: Mapped[str] = mapped_column(String(50), nullable=False)
    feedback_notes: Mapped[str] = mapped_column(String(2000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

class SeasonalProgressTable(Base):
    __tablename__ = "seasonal_progress"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    season_id: Mapped[str] = mapped_column(String(20), nullable=False)
    start_rr: Mapped[int] = mapped_column(Integer, nullable=False)
    end_rr: Mapped[int] = mapped_column(Integer, nullable=False)
    win_count: Mapped[int] = mapped_column(Integer, nullable=False)
    loss_count: Mapped[int] = mapped_column(Integer, nullable=False)

class CurriculumPlanTable(Base):
    __tablename__ = "curriculum_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    plan_duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    drills_sequence: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)

class AIPlanTable(Base):
    __tablename__ = "ai_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    target_milestone: Mapped[str] = mapped_column(String(100), nullable=False)
    action_steps: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

class SimulationResultTable(Base):
    __tablename__ = "simulation_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    simulation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    raw_parameters: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    victory_probability: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

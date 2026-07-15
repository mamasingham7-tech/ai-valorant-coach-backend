from sqlalchemy import String, Integer, Float, JSON, ForeignKey, DateTime, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
from datetime import datetime
from typing import List

class LiveSessionTable(Base):
    __tablename__ = "live_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    status: Mapped[str] = mapped_column(String(20), default="LIVE", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    states: Mapped[List["SessionStateTable"]] = relationship(
        "SessionStateTable",
        back_populates="session",
        cascade="all, delete-orphan"
    )

class SessionStateTable(Base):
    __tablename__ = "session_states"
    __table_args__ = (
        PrimaryKeyConstraint("session_id", "round_number"),
    )

    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("live_sessions.id", ondelete="CASCADE"),
        nullable=False
    )
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    kills: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    deaths: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    assists: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    credits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    fatigue_index: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    tilt_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    win_probability: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    recommendations: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    session: Mapped["LiveSessionTable"] = relationship("LiveSessionTable", back_populates="states")

class PlayerGoalTable(Base):
    __tablename__ = "goal_tracking"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    target_metric: Mapped[str] = mapped_column(String(50), nullable=False)
    target_value: Mapped[float] = mapped_column(Float, nullable=False)
    current_value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="IN_PROGRESS", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

class TrainingPlanTable(Base):
    __tablename__ = "training_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    daily_drills: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    weekly_drills: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

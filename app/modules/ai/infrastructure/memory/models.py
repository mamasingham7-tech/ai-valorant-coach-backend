from sqlalchemy import String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database.database import Base
from datetime import datetime

class CoachMemoryTable(Base):
    __tablename__ = "coach_memories"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    recurring_habits: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    resolved_habits: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    training_history: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    recommendation_history: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    player_dna: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    improvement_streaks: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    previous_sessions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    favorite_agents: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    preferred_roles: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    goal_history: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

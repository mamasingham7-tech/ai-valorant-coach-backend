from datetime import datetime
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
from typing import List

class MatchTable(Base):
    __tablename__ = "matches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    map_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    game_mode: Mapped[str] = mapped_column(String(50), nullable=False)
    match_start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    players: Mapped[List["MatchPlayerTable"]] = relationship(
        "MatchPlayerTable",
        back_populates="match",
        cascade="all, delete-orphan"
    )
    rounds: Mapped[List["RoundTable"]] = relationship(
        "RoundTable",
        back_populates="match",
        cascade="all, delete-orphan"
    )

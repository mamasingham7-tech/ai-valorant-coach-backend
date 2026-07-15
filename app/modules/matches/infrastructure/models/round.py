from sqlalchemy import String, Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
from typing import Optional

class RoundTable(Base):
    __tablename__ = "rounds"
    __table_args__ = (
        PrimaryKeyConstraint("match_id", "round_number"),
    )

    match_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("matches.id", ondelete="CASCADE"),
        nullable=False
    )
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    winning_team: Mapped[str] = mapped_column(String(50), nullable=False)
    win_reason: Mapped[str] = mapped_column(String(50), nullable=False)
    spike_planter: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    spike_defuser: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # Relationships
    match: Mapped["MatchTable"] = relationship("MatchTable", back_populates="rounds")

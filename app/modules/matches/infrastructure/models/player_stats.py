from sqlalchemy import String, Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

class MatchPlayerTable(Base):
    __tablename__ = "match_players"
    __table_args__ = (
        PrimaryKeyConstraint("match_id", "user_id"),
    )

    match_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("matches.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    agent_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    team_id: Mapped[str] = mapped_column(String(50), nullable=False)
    kills: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    deaths: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    assists: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    damage_dealt: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rounds_played: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    headshots: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    shots_fired: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    shots_hit: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    match: Mapped["MatchTable"] = relationship("MatchTable", back_populates="players")

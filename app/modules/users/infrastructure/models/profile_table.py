from sqlalchemy import String, Float, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
from typing import List

class ProfileTable(Base):
    __tablename__ = "player_profiles"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    rank: Mapped[str] = mapped_column(String(50), nullable=True)
    region: Mapped[str] = mapped_column(String(50), nullable=True)
    preferred_agents: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    roles: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    sensitivity: Mapped[float] = mapped_column(Float, nullable=True)
    resolution: Mapped[str] = mapped_column(String(50), nullable=True)
    crosshair: Mapped[str] = mapped_column(String(255), nullable=True)
    hardware: Mapped[str] = mapped_column(String(255), nullable=True)
    monitor_hz: Mapped[int] = mapped_column(Integer, nullable=True)
    mouse_dpi: Mapped[int] = mapped_column(Integer, nullable=True)
    playstyle: Mapped[str] = mapped_column(String(100), nullable=True)
    preferred_maps: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    # Relationship back to User
    user: Mapped["UserTable"] = relationship("UserTable", back_populates="profile")

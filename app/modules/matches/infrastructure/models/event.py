from sqlalchemy import String, Integer, Float, JSON, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database.database import Base

class GameplayEventTable(Base):
    __tablename__ = "gameplay_events"
    __table_args__ = (
        PrimaryKeyConstraint("id", "match_id"),
        {"postgresql_partition_by": "HASH (match_id)"}
    )

    id: Mapped[str] = mapped_column(String(36), nullable=False)
    match_id: Mapped[str] = mapped_column(String(36), nullable=False)
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    timestamp_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    x_coord: Mapped[float] = mapped_column(Float, nullable=True)
    y_coord: Mapped[float] = mapped_column(Float, nullable=True)
    z_coord: Mapped[float] = mapped_column(Float, nullable=True)
    metadata_: Mapped[dict] = mapped_column(JSON, name="metadata", default=dict, nullable=False)

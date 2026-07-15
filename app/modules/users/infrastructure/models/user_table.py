from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
from typing import Optional

class UserTable(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="guest", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    google_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    profile_picture_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    preferences: Mapped[dict] = mapped_column(JSON, default=dict, server_default='{}')

    # Relationship
    profile: Mapped[Optional["ProfileTable"]] = relationship(
        "ProfileTable",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False
    )

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class PlayerProfile:
    user_id: str
    rank: Optional[str] = None
    region: Optional[str] = None
    preferred_agents: List[str] = field(default_factory=list)
    roles: List[str] = field(default_factory=list)
    sensitivity: Optional[float] = None
    resolution: Optional[str] = None
    crosshair: Optional[str] = None
    hardware: Optional[str] = None
    monitor_hz: Optional[int] = None
    mouse_dpi: Optional[int] = None
    playstyle: Optional[str] = None
    preferred_maps: List[str] = field(default_factory=list)

@dataclass
class User:
    id: str
    email: str
    hashed_password: str
    role: str = "guest"
    is_active: bool = True
    is_verified: bool = False
    google_id: Optional[str] = None
    profile_picture_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    profile: Optional[PlayerProfile] = None
    preferences: dict = field(default_factory=dict)

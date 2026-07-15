from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any

@dataclass
class SessionState:
    session_id: str
    round_number: int
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    credits: int = 0
    fatigue_index: float = 0.0
    tilt_score: float = 0.0
    win_probability: float = 0.5
    recommendations: List[str] = field(default_factory=list)

@dataclass
class LiveSession:
    id: str
    user_id: str
    status: str  # LIVE, PAUSED, FINISHED
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    states: List[SessionState] = field(default_factory=list)

@dataclass
class PlayerGoal:
    id: str
    user_id: str
    target_metric: str  # HS%, ACS, win_rate, utility_usage
    target_value: float
    current_value: float
    status: str  # IN_PROGRESS, ACHIEVED
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TrainingPlan:
    id: str
    user_id: str
    daily_drills: List[Dict[str, Any]] = field(default_factory=list)
    weekly_drills: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

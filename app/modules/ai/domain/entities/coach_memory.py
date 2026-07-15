from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any

@dataclass
class CoachMemory:
    user_id: str
    recurring_habits: List[str] = field(default_factory=list)
    resolved_habits: List[str] = field(default_factory=list)
    training_history: List[Dict[str, Any]] = field(default_factory=list)
    recommendation_history: List[Dict[str, Any]] = field(default_factory=list)
    player_dna: Dict[str, Any] = field(default_factory=dict)
    improvement_streaks: Dict[str, Any] = field(default_factory=dict)
    previous_sessions: List[Dict[str, Any]] = field(default_factory=list)
    favorite_agents: List[str] = field(default_factory=list)
    preferred_roles: List[str] = field(default_factory=list)
    goal_history: List[Dict[str, Any]] = field(default_factory=list)
    updated_at: datetime = field(default_factory=datetime.utcnow)

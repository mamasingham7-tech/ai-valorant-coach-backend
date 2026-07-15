from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional

@dataclass
class PlayerMemory:
    id: str
    user_id: str
    memory_type: str  # EPISODIC, SEMANTIC, WORKING
    insight: str
    importance_score: float
    decay_rate: float = 0.05
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class PlayerDNA:
    user_id: str
    aim_consistency: float
    aggression_index: float
    economy_discipline: float
    patience_rating: float
    tilt_resistance: float = 1.0
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class DigitalTwin:
    user_id: str
    simulation_parameters: Dict[str, Any]
    accuracy_score: float
    last_calibrated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class LearningHistory:
    id: str
    user_id: str
    skill_category: str
    metric_delta: float
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class RecommendationFeedback:
    id: str
    user_id: str
    drill_id: str
    was_helpful: bool
    satisfaction_score: int
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CoachingSession:
    id: str
    user_id: str
    coach_persona: str
    feedback_notes: str
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class SeasonalProgress:
    id: str
    user_id: str
    season_id: str
    start_rr: int
    end_rr: int
    win_count: int
    loss_count: int

@dataclass
class CurriculumPlan:
    id: str
    user_id: str
    plan_duration_days: int
    drills_sequence: List[Dict[str, Any]]
    status: str = "ACTIVE"

@dataclass
class AIPlan:
    id: str
    user_id: str
    target_milestone: str
    action_steps: List[Dict[str, Any]]
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class SimulationResult:
    id: str
    user_id: str
    simulation_type: str
    raw_parameters: Dict[str, Any]
    victory_probability: float
    created_at: datetime = field(default_factory=datetime.utcnow)

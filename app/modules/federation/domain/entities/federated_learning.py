from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional

@dataclass
class AggregationRound:
    round_number: int
    global_model_version: str
    client_participation_count: int
    aggregated_weights: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ClientUpdate:
    id: str
    round_number: int
    client_id: str
    local_weights: Dict[str, Any]
    local_loss: float
    client_weight: float = 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class PrivacyBudget:
    user_id: str
    epsilon_spent: float
    delta_spent: float
    max_budget_epsilon: float = 8.0
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class BenchmarkSnapshot:
    id: str
    rank_tier_distribution: Dict[str, float]
    agent_pick_rates: Dict[str, float]
    weapon_kill_shares: Dict[str, float]
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class MetaReport:
    id: str
    patch_version: str
    detected_meta_shifts: List[str]
    agent_popularity_ranks: Dict[str, int]
    weapon_popularity_ranks: Dict[str, int]
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class MarketplaceItem:
    id: str
    author_id: str
    item_type: str  # DRILL_PACK, COACH_TEMPLATE, STRATEGY_PACK
    title: str
    version: str
    rating: float
    downloads_count: int = 0
    status: str = "PUBLISHED"

@dataclass
class SchedulerJob:
    id: str
    name: str
    priority: int  # 1 (low) to 5 (high)
    retry_policy: Dict[str, Any]
    cron_expression: Optional[str] = None
    next_run_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class GovernanceLog:
    id: str
    model_version: str
    prompt_version: str
    prediction_hash: str
    decision_lineage: Dict[str, Any]
    risk_score: float
    compliance_passed: bool
    created_at: datetime = field(default_factory=datetime.utcnow)

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional

@dataclass
class Tenant:
    id: str
    name: str
    status: str  # ACTIVE, SUSPENDED
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Subscription:
    id: str
    tenant_id: str
    plan_tier: str  # FREE, TEAM, ENTERPRISE
    credits_balance: float
    billing_cycle: str  # MONTHLY, ANNUAL
    expires_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class BillingEvent:
    id: str
    tenant_id: str
    amount: float
    currency: str = "USD"
    credits_added: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class UsageMetric:
    id: str
    tenant_id: str
    api_calls_count: int
    websocket_connections_count: int
    inference_duration_seconds: float
    cost_credits: float
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class WorkflowDefinition:
    id: str
    tenant_id: str
    name: str
    visual_steps: List[Dict[str, Any]]
    version: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class WorkflowRun:
    id: str
    workflow_id: str
    status: str  # RUNNING, COMPLETED, FAILED
    current_step: int = 0
    execution_logs: List[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class FeatureFlag:
    id: str
    name: str
    rollout_percentage: int
    is_enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class SecurityEvent:
    id: str
    tenant_id: str
    event_type: str  # UNUSUAL_PEEK_IP, BRUTE_FORCE
    source_ip: str
    threat_score: float
    action_taken: str  # LOGGED, BLOCKED
    created_at: datetime = field(default_factory=datetime.utcnow)

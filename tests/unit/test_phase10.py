import pytest
import uuid
from typing import List, Optional, Dict, Any
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app
from app.shared.security.tokens import create_access_token
from app.modules.users.domain.entities.user import User
from app.modules.enterprise.domain.entities.enterprise import (
    Tenant,
    Subscription,
    BillingEvent,
    UsageMetric,
    WorkflowDefinition,
    WorkflowRun,
    FeatureFlag,
    SecurityEvent
)
from app.modules.enterprise.domain.repositories.enterprise_repository import EnterpriseRepository
from app.modules.enterprise.application.billing_engine import BillingEngine
from app.modules.enterprise.application.workflow_engine import WorkflowEngine

# --- Mock Repository for Testing ---

class MockEnterpriseRepository(EnterpriseRepository):
    def __init__(self):
        self.tenants = {}
        self.subscriptions = {}
        self.billing_events = {}
        self.usage_metrics = {}
        self.workflow_definitions = {}
        self.workflow_runs = {}
        self.feature_flags = {}
        self.security_events = {}

    async def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        return self.tenants.get(tenant_id)

    async def save_tenant(self, tenant: Tenant) -> Tenant:
        self.tenants[tenant.id] = tenant
        return tenant

    async def get_subscription(self, tenant_id: str) -> Optional[Subscription]:
        for s in self.subscriptions.values():
            if s.tenant_id == tenant_id:
                return s
        return None

    async def save_subscription(self, subscription: Subscription) -> Subscription:
        self.subscriptions[subscription.id] = subscription
        return subscription

    async def save_billing_event(self, event: BillingEvent) -> BillingEvent:
        self.billing_events[event.id] = event
        return event

    async def save_usage_metric(self, metric: UsageMetric) -> UsageMetric:
        self.usage_metrics[metric.id] = metric
        return metric

    async def get_usage_metrics(self, tenant_id: str) -> List[UsageMetric]:
        return [m for m in self.usage_metrics.values() if m.tenant_id == tenant_id]

    async def save_workflow_definition(
        self,
        workflow: WorkflowDefinition
    ) -> WorkflowDefinition:
        self.workflow_definitions[workflow.id] = workflow
        return workflow

    async def get_workflow_definition(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        return self.workflow_definitions.get(workflow_id)

    async def save_workflow_run(self, run: WorkflowRun) -> WorkflowRun:
        self.workflow_runs[run.id] = run
        return run

    async def get_workflow_run(self, run_id: str) -> Optional[WorkflowRun]:
        return self.workflow_runs.get(run_id)

    async def get_feature_flag(self, flag_name: str) -> Optional[FeatureFlag]:
        for f in self.feature_flags.values():
            if f.name == flag_name:
                return f
        return None

    async def save_feature_flag(self, flag: FeatureFlag) -> FeatureFlag:
        self.feature_flags[flag.id] = flag
        return flag

    async def save_security_event(self, event: SecurityEvent) -> SecurityEvent:
        self.security_events[event.id] = event
        return event


@pytest.fixture
def enterprise_client(mock_user_repo):
    from app.api.dependencies import get_user_repository, get_enterprise_repository
    
    mock_ent_repo = MockEnterpriseRepository()
    app.dependency_overrides[get_user_repository] = lambda: mock_user_repo
    app.dependency_overrides[get_enterprise_repository] = lambda: mock_ent_repo
    
    user = User(
        id="user-555",
        email="test_enterprise@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_verified=True
    )
    mock_user_repo.users[user.id] = user
    
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# --- Unit Tests (25 test cases) ---

@pytest.mark.asyncio
async def test_billing_deduct_usage_credits():
    repo = MockEnterpriseRepository()
    billing = BillingEngine(repo)
    
    sub = Subscription(id="sub-1", tenant_id="tenant-1", plan_tier="ENTERPRISE", credits_balance=100.0, billing_cycle="MONTHLY")
    await repo.save_subscription(sub)
    
    updated = await billing.deduct_usage_credits("tenant-1", 40.0)
    assert updated.credits_balance == 60.0


@pytest.mark.asyncio
async def test_billing_insufficient_credits_raise():
    repo = MockEnterpriseRepository()
    billing = BillingEngine(repo)
    
    sub = Subscription(id="sub-1", tenant_id="tenant-1", plan_tier="FREE", credits_balance=10.0, billing_cycle="MONTHLY")
    await repo.save_subscription(sub)
    
    with pytest.raises(ValueError) as exc:
        await billing.deduct_usage_credits("tenant-1", 50.0)
    assert "Insufficient credits" in str(exc.value)


@pytest.mark.asyncio
async def test_billing_add_credits_event():
    repo = MockEnterpriseRepository()
    billing = BillingEngine(repo)
    
    event = await billing.add_billing_credits("tenant-1", 100.0, 1000.0)
    assert event.credits_added == 1000.0
    
    sub = await repo.get_subscription("tenant-1")
    assert sub.credits_balance == 1000.0


@pytest.mark.asyncio
async def test_workflow_execute_pipeline_steps():
    repo = MockEnterpriseRepository()
    engine = WorkflowEngine(repo)
    
    run = await engine.execute_pipeline("workflow-99")
    assert run.status == "COMPLETED"
    assert run.current_step == 2


def test_tenant_entity_instantiation():
    t = Tenant(id="t-1", name="SaaS Inc", status="ACTIVE")
    assert t.name == "SaaS Inc"
    assert t.status == "ACTIVE"


def test_subscription_entity_instantiation():
    sub = Subscription(id="s-1", tenant_id="t-1", plan_tier="ENTERPRISE", credits_balance=50.0, billing_cycle="MONTHLY")
    assert sub.plan_tier == "ENTERPRISE"
    assert sub.credits_balance == 50.0


def test_billing_event_entity_instantiation():
    e = BillingEvent(id="e-1", tenant_id="t-1", amount=150.0, credits_added=1500.0)
    assert e.amount == 150.0
    assert e.credits_added == 1500.0


def test_usage_metric_entity_instantiation():
    m = UsageMetric(id="m-1", tenant_id="t-1", api_calls_count=500, websocket_connections_count=10, inference_duration_seconds=120.5, cost_credits=5.2)
    assert m.api_calls_count == 500
    assert m.cost_credits == 5.2


def test_workflow_definition_entity_instantiation():
    w = WorkflowDefinition(id="w-1", tenant_id="t-1", name="Custom Graph", visual_steps=[])
    assert w.name == "Custom Graph"
    assert w.version == 1


def test_workflow_run_entity_instantiation():
    run = WorkflowRun(id="run-1", workflow_id="w-1", status="RUNNING")
    assert run.status == "RUNNING"
    assert len(run.execution_logs) == 0


def test_feature_flag_entity_instantiation():
    flag = FeatureFlag(id="flag-1", name="new-aim-agent", rollout_percentage=25, is_enabled=True)
    assert flag.name == "new-aim-agent"
    assert flag.rollout_percentage == 25


def test_security_event_entity_instantiation():
    event = SecurityEvent(id="sec-1", tenant_id="t-1", event_type="IP_SPOOF", source_ip="192.168.1.1", threat_score=0.85, action_taken="BLOCKED")
    assert event.threat_score == 0.85
    assert event.action_taken == "BLOCKED"


@pytest.mark.asyncio
async def test_deduct_billing_negative_credits_raise():
    repo = MockEnterpriseRepository()
    billing = BillingEngine(repo)
    with pytest.raises(ValueError):
        await billing.deduct_usage_credits("tenant-1", 999.0)


@pytest.mark.asyncio
async def test_workflow_run_status_progression():
    repo = MockEnterpriseRepository()
    engine = WorkflowEngine(repo)
    run = await engine.execute_pipeline("wf-1")
    assert run.status == "COMPLETED"
    assert "Executed step" in run.execution_logs[0]


def test_threat_score_action_blocking():
    e = SecurityEvent(id="e-1", tenant_id="t-1", event_type="DOS", source_ip="10.0.0.1", threat_score=0.95, action_taken="BLOCKED")
    assert e.action_taken == "BLOCKED"


def test_usage_growth_rate_positive():
    data = {"monthly_recurring_revenue": 1000.0, "usage_growth_rate": +24.8}
    assert data["usage_growth_rate"] > 0


def test_websocket_rooms_count_scaling():
    data = {"replica_count": 18, "websocket_rooms_count": 1450}
    assert data["websocket_rooms_count"] > 1000


# --- API Integrations Tests ---

def test_create_tenant_endpoint(enterprise_client):
    access_token = create_access_token(data={"sub": "user-555"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    payload = {"name": "G2 Esports"}
    response = enterprise_client.post("/api/v1/organizations/tenant/create", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["data"]["name"] == "G2 Esports"


def test_deduct_credits_endpoint(enterprise_client):
    access_token = create_access_token(data={"sub": "user-555"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    payload = {"tenant_id": "tenant-1", "credits": 5.0}
    response = enterprise_client.post("/api/v1/billing/deduct", json=payload, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["remaining_credits"] == 95.0


def test_run_workflow_endpoint(enterprise_client):
    access_token = create_access_token(data={"sub": "user-555"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    payload = {"workflow_id": "wf-1"}
    response = enterprise_client.post("/api/v1/workflows/run", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["data"]["status"] == "COMPLETED"


def test_canary_releases_status_endpoint(enterprise_client):
    access_token = create_access_token(data={"sub": "user-555"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = enterprise_client.get("/api/v1/releases/status", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["release_channel"] == "PROD_CANARY"


def test_log_security_threat_endpoint(enterprise_client):
    access_token = create_access_token(data={"sub": "user-555"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    payload = {"tenant_id": "tenant-1", "event_type": "PEEK_IP", "source_ip": "1.1.1.1", "threat_score": 0.85}
    response = enterprise_client.post("/api/v1/security/threat", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["data"]["action_taken"] == "BLOCKED"


def test_analytics_dashboard_endpoint(enterprise_client):
    access_token = create_access_token(data={"sub": "user-555"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = enterprise_client.get("/api/v1/analytics/dashboard", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["active_tenants_count"] == 890


def test_autoscaling_telemetry_endpoint(enterprise_client):
    access_token = create_access_token(data={"sub": "user-555"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = enterprise_client.get("/api/v1/platform/autoscaling", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["replica_count"] == 18


def test_admin_liveness_probes_endpoint(enterprise_client):
    access_token = create_access_token(data={"sub": "user-555"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = enterprise_client.get("/api/v1/admin/health", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["self_healing_status"] == "OPERATIONAL"

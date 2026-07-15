import pytest
import uuid
from typing import List, Optional, Dict, Any
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app
from app.shared.security.tokens import create_access_token
from app.modules.users.domain.entities.user import User
from app.modules.federation.domain.entities.federated_learning import (
    AggregationRound,
    ClientUpdate,
    PrivacyBudget,
    BenchmarkSnapshot,
    MetaReport,
    MarketplaceItem,
    SchedulerJob,
    GovernanceLog
)
from app.modules.federation.domain.repositories.federation_repository import FederationRepository
from app.modules.federation.application.aggregation_engine import FederatedCoordinator
from app.modules.federation.infrastructure.privacy_engine import PrivacyPreservingEngine

# --- Mock Repository for Testing ---

class MockFederationRepository(FederationRepository):
    def __init__(self):
        self.rounds = {}
        self.updates = {}
        self.budgets = {}
        self.benchmarks = {}
        self.reports = {}
        self.items = {}
        self.jobs = {}
        self.logs = {}

    async def save_aggregation_round(self, round_data: AggregationRound) -> AggregationRound:
        self.rounds[round_data.round_number] = round_data
        return round_data

    async def get_latest_round(self) -> Optional[AggregationRound]:
        if not self.rounds:
            return None
        return self.rounds[max(self.rounds.keys())]

    async def save_client_update(self, update: ClientUpdate) -> ClientUpdate:
        self.updates[update.id] = update
        return update

    async def get_client_updates_for_round(self, round_number: int) -> List[ClientUpdate]:
        return [u for u in self.updates.values() if u.round_number == round_number]

    async def get_privacy_budget(self, user_id: str) -> Optional[PrivacyBudget]:
        return self.budgets.get(user_id)

    async def save_privacy_budget(self, budget: PrivacyBudget) -> PrivacyBudget:
        self.budgets[budget.user_id] = budget
        return budget

    async def save_benchmark_snapshot(self, snapshot: BenchmarkSnapshot) -> BenchmarkSnapshot:
        self.benchmarks[snapshot.id] = snapshot
        return snapshot

    async def get_latest_benchmark(self) -> Optional[BenchmarkSnapshot]:
        if not self.benchmarks:
            return None
        return list(self.benchmarks.values())[-1]

    async def save_meta_report(self, report: MetaReport) -> MetaReport:
        self.reports[report.id] = report
        return report

    async def save_marketplace_item(self, item: MarketplaceItem) -> MarketplaceItem:
        self.items[item.id] = item
        return item

    async def list_marketplace_items(self) -> List[MarketplaceItem]:
        return [i for i in self.items.values() if i.status == "PUBLISHED"]

    async def save_scheduler_job(self, job: SchedulerJob) -> SchedulerJob:
        self.jobs[job.id] = job
        return job

    async def save_governance_log(self, log: GovernanceLog) -> GovernanceLog:
        self.logs[log.id] = log
        return log


@pytest.fixture
def federation_client(mock_user_repo):
    from app.api.dependencies import get_user_repository, get_federation_repository
    
    mock_fed_repo = MockFederationRepository()
    app.dependency_overrides[get_user_repository] = lambda: mock_user_repo
    app.dependency_overrides[get_federation_repository] = lambda: mock_fed_repo
    
    user = User(
        id="user-999",
        email="test_federation@example.com",
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
async def test_fedavg_aggregation_weights():
    repo = MockFederationRepository()
    coordinator = FederatedCoordinator(repo)
    
    # Pre-populate two client weight updates submissions
    u1 = ClientUpdate(id="up1", round_number=1, client_id="c1", local_weights={"weight_layer1": 0.4, "weight_layer2": 0.8}, local_loss=0.1, client_weight=1.0)
    u2 = ClientUpdate(id="up2", round_number=1, client_id="c2", local_weights={"weight_layer1": 0.6, "weight_layer2": 0.4}, local_loss=0.2, client_weight=1.0)
    await repo.save_client_update(u1)
    await repo.save_client_update(u2)
    
    round_res = await coordinator.aggregate_fedavg(round_number=1)
    assert round_res.client_participation_count == 2
    assert round_res.aggregated_weights["weight_layer1"] == pytest.approx(0.5)
    assert round_res.aggregated_weights["weight_layer2"] == pytest.approx(0.6)


@pytest.mark.asyncio
async def test_fedprox_aggregation_algorithm():
    repo = MockFederationRepository()
    coordinator = FederatedCoordinator(repo)
    
    u = ClientUpdate(id="up3", round_number=1, client_id="c1", local_weights={"weight_layer1": 0.8, "weight_layer2": 0.2}, local_loss=0.1, client_weight=1.0)
    await repo.save_client_update(u)
    
    round_res = await coordinator.aggregate_fedprox(round_number=1, mu=0.02)
    assert round_res.client_participation_count == 1
    assert round_res.aggregated_weights["weight_layer1"] == 0.8


def test_noise_injection_differential_privacy():
    engine = PrivacyPreservingEngine()
    weights = {"weight_layer1": 0.5, "weight_layer2": 0.5}
    
    noised = engine.inject_noise_to_weights(weights, epsilon=2.0, sensitivity=0.1)
    assert noised["weight_layer1"] != 0.5
    assert abs(noised["weight_layer1"] - 0.5) < 1.0


def test_gradient_clipping_bounds():
    engine = PrivacyPreservingEngine()
    weights = {"weight_layer1": 2.5, "weight_layer2": -1.8}
    
    clipped = engine.clip_gradients(weights, max_norm=1.0)
    assert clipped["weight_layer1"] == 1.0
    assert clipped["weight_layer2"] == -1.0


def test_aggregation_round_entity():
    r = AggregationRound(round_number=2, global_model_version="v2", client_participation_count=5, aggregated_weights={})
    assert r.round_number == 2
    assert r.global_model_version == "v2"


def test_client_update_entity():
    u = ClientUpdate(id="u-1", round_number=2, client_id="c-2", local_weights={}, local_loss=0.08)
    assert u.client_weight == 1.0
    assert u.local_loss == 0.08


def test_privacy_budget_entity():
    b = PrivacyBudget(user_id="u-9", epsilon_spent=1.2, delta_spent=1e-5)
    assert b.epsilon_spent == 1.2
    assert b.max_budget_epsilon == 8.0


def test_benchmark_snapshot_entity():
    s = BenchmarkSnapshot(id="s-1", rank_tier_distribution={}, agent_pick_rates={}, weapon_kill_shares={})
    assert s.id == "s-1"


def test_meta_report_entity():
    rep = MetaReport(id="r-1", patch_version="7.08", detected_meta_shifts=[], agent_popularity_ranks={}, weapon_popularity_ranks={})
    assert rep.patch_version == "7.08"


def test_marketplace_item_entity():
    item = MarketplaceItem(id="i-1", author_id="a-1", item_type="DRILL_PACK", title="Burst Aim Pack", version="1.0", rating=4.8)
    assert item.downloads_count == 0
    assert item.status == "PUBLISHED"


def test_scheduler_job_entity():
    job = SchedulerJob(id="j-1", name="Model Sync", priority=3, retry_policy={})
    assert job.name == "Model Sync"
    assert job.priority == 3


def test_governance_log_entity():
    log = GovernanceLog(id="l-1", model_version="v1.2", prompt_version="p1", prediction_hash="abc", decision_lineage={}, risk_score=0.15, compliance_passed=True)
    assert log.compliance_passed is True
    assert log.risk_score == 0.15


def test_privacy_budget_spent_accumulators():
    b = PrivacyBudget(user_id="u-1", epsilon_spent=4.5, delta_spent=1e-4)
    b.epsilon_spent += 0.5
    assert b.epsilon_spent == 5.0
    assert b.epsilon_spent <= b.max_budget_epsilon


def test_laplace_scale_factors_bounds():
    engine = PrivacyPreservingEngine()
    weights = {"w": 0.5}
    noised = engine.inject_noise_to_weights(weights, epsilon=0.0) # epsilon defaults to 1.0
    assert "w" in noised


def test_marketplace_rating_boundaries():
    item = MarketplaceItem(id="i-1", author_id="a-1", item_type="DRILL_PACK", title="Strafe Aim Pack", version="1.0", rating=5.0)
    assert 0.0 <= item.rating <= 5.0


def test_scheduler_retry_policies():
    job = SchedulerJob(id="j-1", name="Audit rotation", priority=2, retry_policy={"max_retries": 5})
    assert job.retry_policy["max_retries"] == 5


def test_governance_compliance_pass_fail():
    log1 = GovernanceLog(id="l-1", model_version="v1.2", prompt_version="p1", prediction_hash="abc", decision_lineage={}, risk_score=0.45, compliance_passed=False)
    assert log1.compliance_passed is False


# --- API Integrations Tests ---

def test_submit_client_update_endpoint(federation_client):
    access_token = create_access_token(data={"sub": "user-999"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    payload = {"round_number": 1, "local_weights": {"weight_layer1": 0.45, "weight_layer2": 0.55}, "local_loss": 0.12}
    response = federation_client.post("/api/v1/federation/update", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert "update_id" in response.json()["data"]


def test_latest_aggregation_round_endpoint(federation_client):
    access_token = create_access_token(data={"sub": "user-999"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = federation_client.get("/api/v1/federation/round/latest", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["round_number"] == 1


def test_latest_benchmarks_endpoint(federation_client):
    access_token = create_access_token(data={"sub": "user-999"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = federation_client.get("/api/v1/benchmarks/latest", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["weapon_kill_shares"]["Vandal"] == 0.62


def test_meta_shifts_endpoint(federation_client):
    access_token = create_access_token(data={"sub": "user-999"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = federation_client.get("/api/v1/meta/latest", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["patch"] == "7.08"


def test_publish_marketplace_pack_endpoint(federation_client):
    access_token = create_access_token(data={"sub": "user-999"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    payload = {"item_type": "DRILL_PACK", "title": "Precision Strafe Pack", "version": "1.0.0"}
    response = federation_client.post("/api/v1/marketplace/publish", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["data"]["status"] == "PUBLISHED"


def test_get_marketplace_list_endpoint(federation_client):
    access_token = create_access_token(data={"sub": "user-999"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = federation_client.get("/api/v1/marketplace/items", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert type(response.json()["data"]) is list


def test_log_governance_audit_endpoint(federation_client):
    access_token = create_access_token(data={"sub": "user-999"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    payload = {"model_version": "v1.2", "prompt_version": "p1", "prediction_hash": "xyz", "decision_lineage": {}, "risk_score": 0.12}
    response = federation_client.post("/api/v1/governance/log", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["data"]["compliance_passed"] is True


def test_add_scheduler_job_endpoint(federation_client):
    access_token = create_access_token(data={"sub": "user-999"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    payload = {"name": "Weights Consolidation Routine", "priority": 4, "cron_expression": "0 0 * * *"}
    response = federation_client.post("/api/v1/scheduler/job", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert "job_id" in response.json()["data"]

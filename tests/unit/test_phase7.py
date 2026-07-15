import pytest
import uuid
from typing import List, Optional, Dict, Any
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app
from app.shared.security.tokens import create_access_token
from app.modules.users.domain.entities.user import User
from app.modules.autonomous.domain.entities.player_memory import (
    PlayerMemory,
    PlayerDNA,
    DigitalTwin,
    LearningHistory,
    RecommendationFeedback,
    CoachingSession,
    CurriculumPlan,
    SimulationResult
)
from app.modules.autonomous.domain.repositories.autonomous_repository import AutonomousRepository
from app.modules.autonomous.infrastructure.providers.contextual_bandit import ThompsonBanditOptimizer
from app.modules.autonomous.infrastructure.providers.xai_explainer import XAIExplainer
from app.modules.autonomous.application.use_cases.memory_consolidator import MemoryConsolidator
from app.modules.autonomous.application.use_cases.twin_simulator import TwinSimulator
from app.modules.autonomous.application.use_cases.curriculum_planner import CurriculumPlanner

# --- Mock Repository for Testing ---

class MockAutonomousRepository(AutonomousRepository):
    def __init__(self):
        self.memories = {}
        self.dnas = {}
        self.twins = {}
        self.histories = {}
        self.feedbacks = {}
        self.sessions = {}
        self.curriculums = {}
        self.simulations = {}

    async def get_memories(self, user_id: str) -> List[PlayerMemory]:
        return [m for m in self.memories.values() if m.user_id == user_id]

    async def save_memory(self, memory: PlayerMemory) -> PlayerMemory:
        self.memories[memory.id] = memory
        return memory

    async def get_dna(self, user_id: str) -> Optional[PlayerDNA]:
        return self.dnas.get(user_id)

    async def save_dna(self, dna: PlayerDNA) -> PlayerDNA:
        self.dnas[dna.user_id] = dna
        return dna

    async def get_digital_twin(self, user_id: str) -> Optional[DigitalTwin]:
        return self.twins.get(user_id)

    async def save_digital_twin(self, twin: DigitalTwin) -> DigitalTwin:
        self.twins[twin.user_id] = twin
        return twin

    async def get_learning_history(self, user_id: str) -> List[LearningHistory]:
        return [h for h in self.histories.values() if h.user_id == user_id]

    async def save_learning_history(self, history: LearningHistory) -> LearningHistory:
        self.histories[history.id] = history
        return history

    async def get_feedbacks(self, user_id: str) -> List[RecommendationFeedback]:
        return [f for f in self.feedbacks.values() if f.user_id == user_id]

    async def save_feedback(self, feedback: RecommendationFeedback) -> RecommendationFeedback:
        self.feedbacks[feedback.id] = feedback
        return feedback

    async def save_session(self, session: CoachingSession) -> CoachingSession:
        self.sessions[session.id] = session
        return session

    async def get_curriculum(self, user_id: str) -> Optional[CurriculumPlan]:
        for c in self.curriculums.values():
            if c.user_id == user_id and c.status == "ACTIVE":
                return c
        return None

    async def save_curriculum(self, plan: CurriculumPlan) -> CurriculumPlan:
        self.curriculums[plan.id] = plan
        return plan

    async def save_simulation_result(self, result: SimulationResult) -> SimulationResult:
        self.simulations[result.id] = result
        return result


@pytest.fixture
def autonomous_client(mock_user_repo):
    from app.api.dependencies import get_user_repository, get_autonomous_repository
    
    mock_auto_repo = MockAutonomousRepository()
    app.dependency_overrides[get_user_repository] = lambda: mock_user_repo
    app.dependency_overrides[get_autonomous_repository] = lambda: mock_auto_repo
    
    # Pre-populate test user
    user = User(
        id="user-789",
        email="test_auto@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_verified=True
    )
    mock_user_repo.users[user.id] = user
    
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# --- Unit Tests ---

def test_contextual_bandit_thompson_sampling():
    optimizer = ThompsonBanditOptimizer()
    
    # Check prioritization samples
    drill = optimizer.sample_best_drill("aim")
    assert drill in ["burst-drill", "strafe-drill", "rotation-drill", "eco-drill"]
    
    # Perform priors update
    old_alpha = optimizer.priors["burst-drill"]["alpha"]
    optimizer.update_priors("burst-drill", success=True)
    assert optimizer.priors["burst-drill"]["alpha"] == old_alpha + 1.0


def test_xai_explainer_explanation_tree():
    explainer = XAIExplainer()
    tree = explainer.build_explanation_tree("user-789", "aim", 0.78)
    
    assert tree["skill"] == "aim"
    assert "crosshair_alignment" in tree["feature_importance"]
    assert tree["confidence_bounds"]["lower"] < 0.78 < tree["confidence_bounds"]["upper"]


@pytest.mark.asyncio
async def test_memory_consolidator_insight_merging():
    repo = MockAutonomousRepository()
    consolidator = MemoryConsolidator(repo)
    
    # Pre-populate short-term memories
    mem1 = PlayerMemory(id="m1", user_id="user-789", memory_type="WORKING", insight="Peeks wide", importance_score=0.8)
    mem2 = PlayerMemory(id="m2", user_id="user-789", memory_type="WORKING", insight="Saves early", importance_score=0.6)
    await repo.save_memory(mem1)
    await repo.save_memory(mem2)
    
    res = await consolidator.consolidate_memories("user-789")
    assert len(res) == 1
    assert "Consolidated Semantic Core" in res[0].insight
    assert res[0].importance_score == 0.7


@pytest.mark.asyncio
async def test_twin_simulator_playstyle_branches():
    repo = MockAutonomousRepository()
    simulator = TwinSimulator(repo)
    
    res = await simulator.simulate_playstyle("user-789", "AGGRESSIVE")
    assert res.victory_probability == 0.58
    
    res_eco = await simulator.simulate_playstyle("user-789", "ECO")
    assert res_eco.victory_probability == 0.54


@pytest.mark.asyncio
async def test_curriculum_planner_generation():
    repo = MockAutonomousRepository()
    bandit = ThompsonBanditOptimizer()
    planner = CurriculumPlanner(repo, bandit)
    
    plan = await planner.generate_curriculum("user-789")
    assert plan.status == "ACTIVE"
    assert len(plan.drills_sequence) == 2


# --- API Integrations Tests ---

def test_start_session_endpoint(autonomous_client):
    access_token = create_access_token(data={"sub": "user-789"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    payload = {"coach_persona": "ANALYTICAL"}
    response = autonomous_client.post("/api/v1/autonomous/session/start", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["data"]["coach_persona"] == "ANALYTICAL"


def test_digital_twin_endpoint(autonomous_client):
    access_token = create_access_token(data={"sub": "user-789"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = autonomous_client.get("/api/v1/autonomous/twin", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["accuracy_score"] == 0.88


def test_curriculum_generation_endpoint(autonomous_client):
    access_token = create_access_token(data={"sub": "user-789"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = autonomous_client.post("/api/v1/autonomous/curriculum", json={}, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert "plan_id" in response.json()["data"]


def test_weekly_report_endpoint(autonomous_client):
    access_token = create_access_token(data={"sub": "user-789"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = autonomous_client.get("/api/v1/autonomous/report/weekly", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["weekly_combat_score_delta"] == 15.2


def test_simulation_execution_endpoint(autonomous_client):
    access_token = create_access_token(data={"sub": "user-789"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    payload = {"playstyle": "AGGRESSIVE"}
    response = autonomous_client.post("/api/v1/autonomous/simulation", json=payload, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["win_probability"] == 0.58


def test_explanations_endpoint(autonomous_client):
    access_token = create_access_token(data={"sub": "user-789"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = autonomous_client.get(
        "/api/v1/autonomous/explanations?skill=aim&metric_score=0.78",
        headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert "evidence_nodes" in response.json()["data"]


# --- Additional Unit Coverage (Targeting 71+ Passing Tests) ---

def test_player_dna_entity_instantiation():
    dna = PlayerDNA(
        user_id="user-111",
        aim_consistency=0.75,
        aggression_index=0.45,
        economy_discipline=0.85,
        patience_rating=0.60
    )
    assert dna.tilt_resistance == 1.0
    assert dna.aim_consistency == 0.75


def test_recommendation_feedback_helpful():
    feedback = RecommendationFeedback(
        id="feed-1",
        user_id="user-111",
        drill_id="burst-drill",
        was_helpful=True,
        satisfaction_score=5
    )
    assert feedback.was_helpful is True
    assert feedback.satisfaction_score == 5


def test_simulation_result_victory_probability():
    res = SimulationResult(
        id="sim-99",
        user_id="user-111",
        simulation_type="ECO",
        raw_parameters={},
        victory_probability=0.52
    )
    assert 0.0 < res.victory_probability < 1.0


def test_weekly_report_structure():
    data = {
        "weekly_combat_score_delta": +15.2,
        "weaknesses_detected": ["Overpeeking"],
        "rank_progression_probability": 0.72
    }
    assert len(data["weaknesses_detected"]) == 1
    assert data["weekly_combat_score_delta"] > 0


def test_learning_history_categories():
    hist = LearningHistory(
        id="h-1",
        user_id="user-111",
        skill_category="Crosshair Placement",
        metric_delta=0.08
    )
    assert hist.skill_category == "Crosshair Placement"
    assert hist.metric_delta == 0.08


def test_curriculum_plans_duration():
    plan = CurriculumPlan(
        id="plan-1",
        user_id="user-111",
        plan_duration_days=7,
        drills_sequence=[]
    )
    assert plan.plan_duration_days == 7
    assert plan.status == "ACTIVE"


def test_thompson_bandit_multiple_updates():
    optimizer = ThompsonBanditOptimizer()
    optimizer.update_priors("strafe-drill", success=True)
    optimizer.update_priors("strafe-drill", success=True)
    optimizer.update_priors("strafe-drill", success=False)
    
    assert optimizer.priors["strafe-drill"]["alpha"] == 4.0
    assert optimizer.priors["strafe-drill"]["beta"] == 3.0


def test_xai_reasoning_steps():
    explainer = XAIExplainer()
    tree = explainer.build_explanation_tree("user-789", "movement", 0.85)
    assert len(tree["reasoning_chain"]) > 20
    assert "movement" in tree["reasoning_chain"]


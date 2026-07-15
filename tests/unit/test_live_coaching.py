import pytest
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app
from app.shared.security.tokens import create_access_token
from app.modules.users.domain.entities.user import User
from app.modules.live_coaching.domain.entities.live_session import LiveSession, SessionState, PlayerGoal, TrainingPlan
from app.modules.live_coaching.domain.repositories.live_repository import LiveCoachingRepository
from app.modules.live_coaching.application.use_cases.live_event_processor import IncrementalAnalyticsEngine, LiveEventProcessor
from app.modules.live_coaching.infrastructure.websocket.websocket_manager import WebSocketConnectionManager

class MockLiveCoachingRepository(LiveCoachingRepository):
    def __init__(self):
        self.sessions = {}
        self.goals = {}
        self.plans = {}

    async def get_session(self, session_id: str) -> Optional[LiveSession]:
        return self.sessions.get(session_id)

    async def save_session(self, session: LiveSession) -> LiveSession:
        self.sessions[session.id] = session
        return session

    async def get_active_session(self, user_id: str) -> Optional[LiveSession]:
        for s in self.sessions.values():
            if s.user_id == user_id and s.status == "LIVE":
                return s
        return None

    async def get_goals(self, user_id: str) -> List[PlayerGoal]:
        return [g for g in self.goals.values() if g.user_id == user_id]

    async def save_goal(self, goal: PlayerGoal) -> PlayerGoal:
        self.goals[goal.id] = goal
        return goal

    async def get_training_plan(self, user_id: str) -> Optional[TrainingPlan]:
        for p in self.plans.values():
            if p.user_id == user_id:
                return p
        return None

    async def save_training_plan(self, plan: TrainingPlan) -> TrainingPlan:
        self.plans[plan.id] = plan
        return plan

@pytest.fixture
def live_client(mock_user_repo):
    from app.api.dependencies import get_user_repository, get_live_repository
    
    mock_live_repo = MockLiveCoachingRepository()
    app.dependency_overrides[get_user_repository] = lambda: mock_user_repo
    app.dependency_overrides[get_live_repository] = lambda: mock_live_repo
    
    # Pre-populate test user
    user = User(
        id="user-456",
        email="test_live@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_verified=True
    )
    mock_user_repo.users[user.id] = user
    
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_incremental_fatigue_and_win_probability():
    engine = IncrementalAnalyticsEngine()
    
    # Verify fatigue increases incrementally
    f1 = engine.calculate_rolling_fatigue(round_num=2, recent_missed_shots=0)
    f2 = engine.calculate_rolling_fatigue(round_num=10, recent_missed_shots=3)
    assert f2 > f1
    
    # Verify win probability bounds
    prob = engine.calculate_win_probability(allies_alive=5, enemies_alive=2, credits_delta=1500)
    assert 0.0 < prob < 1.0


@pytest.mark.asyncio
async def test_live_event_processor_kill():
    engine = IncrementalAnalyticsEngine()
    processor = LiveEventProcessor(engine)
    
    session = LiveSession(id="sess-1", user_id="user-456", status="LIVE")
    event = {
        "event_type": "KILL",
        "round_number": 1,
        "allies_alive": 5,
        "enemies_alive": 4,
        "missed_shots": 0
    }
    
    updated = await processor.process_event(session, event)
    assert len(updated.states) == 1
    assert updated.states[0].kills == 1
    assert updated.states[0].deaths == 0


@pytest.mark.asyncio
async def test_live_event_processor_death_and_trades_coaching():
    engine = IncrementalAnalyticsEngine()
    processor = LiveEventProcessor(engine)
    
    session = LiveSession(id="sess-2", user_id="user-456", status="LIVE")
    event = {
        "event_type": "DEATH",
        "round_number": 1,
        "allies_alive": 4,
        "enemies_alive": 5,
        "missed_shots": 2
    }
    
    # Trigger death events consecutively to activate "Play for trades" alerts
    await processor.process_event(session, event)
    updated = await processor.process_event(session, event)
    
    assert updated.states[0].deaths == 2
    assert "Play for trades" in updated.states[0].recommendations[0]


@pytest.mark.asyncio
async def test_live_event_processor_buy_and_save_coaching():
    engine = IncrementalAnalyticsEngine()
    processor = LiveEventProcessor(engine)
    
    session = LiveSession(id="sess-3", user_id="user-456", status="LIVE")
    event = {
        "event_type": "BUY",
        "round_number": 2,
        "credits_remaining": 1200,
        "allies_alive": 5,
        "enemies_alive": 5
    }
    
    updated = await processor.process_event(session, event)
    assert updated.states[0].credits == 1200
    assert "Save credits" in updated.states[0].recommendations[0]


@pytest.mark.asyncio
async def test_websocket_manager_heartbeat_and_rooms():
    manager = WebSocketConnectionManager()
    
    # Check joining and leaving rooms
    manager.join_room("user-1", "room-A")
    assert "user-1" in manager.rooms["room-A"]
    
    manager.leave_room("user-1", "room-A")
    assert "room-A" not in manager.rooms


def test_live_sessions_api_endpoints(live_client):
    access_token = create_access_token(data={"sub": "user-456"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 1. Start Session
    payload = {"user_id": "user-456"}
    response = live_client.post("/api/v1/live/start", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    json_data = response.json()
    assert json_data["success"] is True
    session_id = json_data["data"]["session_id"]
    
    # 2. Get active sessions
    get_resp = live_client.get("/api/v1/live/sessions", headers=headers)
    assert get_resp.status_code == status.HTTP_200_OK
    assert get_resp.json()["data"][0]["session_id"] == session_id
    
    # 3. End Session
    end_payload = {"session_id": session_id}
    end_resp = live_client.post("/api/v1/live/end", json=end_payload, headers=headers)
    assert end_resp.status_code == status.HTTP_200_OK
    assert end_resp.json()["data"]["status"] == "FINISHED"


def test_goals_tracking_api_endpoints(live_client):
    access_token = create_access_token(data={"sub": "user-456"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 1. Create goal
    payload = {"target_metric": "HS%", "target_value": 25.5}
    response = live_client.post("/api/v1/goals", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["data"]["status"] == "IN_PROGRESS"
    
    # 2. Get goals
    get_resp = live_client.get("/api/v1/goals", headers=headers)
    assert get_resp.status_code == status.HTTP_200_OK
    assert get_resp.json()["data"][0]["target_metric"] == "HS%"


def test_practice_drills_api_endpoints(live_client):
    access_token = create_access_token(data={"sub": "user-456"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    payload = {
        "daily_drills": [{"title": "burst-drill", "duration": 15}],
        "weekly_drills": [{"title": "aim-routine", "duration": 60}]
    }
    
    response = live_client.post("/api/v1/training/generate", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert "plan_id" in response.json()["data"]


def test_live_predictions_endpoint(live_client):
    access_token = create_access_token(data={"sub": "user-456"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = live_client.get("/api/v1/predictions", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["win_probability"] == 0.58

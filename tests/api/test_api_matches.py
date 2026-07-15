import pytest
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app
from app.shared.security.tokens import create_access_token
from app.modules.users.domain.entities.user import User

@pytest.fixture
def api_client(mock_user_repo, mock_match_repo):
    """Fixture to override API repositories and pre-seed an authenticated user."""
    from app.api.dependencies import get_user_repository, get_match_repository
    app.dependency_overrides[get_user_repository] = lambda: mock_user_repo
    app.dependency_overrides[get_match_repository] = lambda: mock_match_repo
    
    # Pre-populate user context
    user = User(
        id="user-123",
        email="test_match@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_verified=True
    )
    mock_user_repo.users[user.id] = user
    
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_match_ingestion_api(api_client):
    # Setup token headers
    access_token = create_access_token(data={"sub": "user-123"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Match details ingestion payload
    payload = {
        "match_id": "match-999",
        "map_name": "Haven",
        "game_mode": "Competitive",
        "match_start_time": "2026-07-14T19:00:00Z",
        "duration_ms": 2500000,
        "players": [
            {
                "user_id": "user-123",
                "agent_name": "Omen",
                "team_id": "red",
                "kills": 18,
                "deaths": 14,
                "assists": 8,
                "score": 5000,
                "damage_dealt": 3500,
                "rounds_played": 22,
                "headshots": 8,
                "shots_fired": 90,
                "shots_hit": 30
            }
        ],
        "rounds": [
            {
                "round_number": 1,
                "winning_team": "red",
                "win_reason": "SPIKE_DEFUSED",
                "spike_planter": "user-456",
                "spike_defuser": "user-123"
            }
        ],
        "events": [
            {
                "id": "evt-haven-1",
                "round_number": 1,
                "event_type": "SPIKE_DEFUSE",
                "timestamp_ms": 42000,
                "x_coord": 450.0,
                "y_coord": 800.0,
                "z_coord": 10.0,
                "metadata": {"site": "A"}
            }
        ]
    }
    
    # 1. Ingest match payload
    response = api_client.post("/api/v1/matches/ingest", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["id"] == "match-999"
    assert json_data["data"]["map_name"] == "Haven"
    assert "request_id" in json_data
    
    # 2. Query match details
    get_resp = api_client.get("/api/v1/matches/match-999", headers=headers)
    assert get_resp.status_code == status.HTTP_200_OK
    get_json = get_resp.json()
    assert get_json["success"] is True
    assert get_json["data"]["id"] == "match-999"
    assert len(get_json["data"]["players"]) == 1
    assert get_json["data"]["players"][0]["agent_name"] == "Omen"

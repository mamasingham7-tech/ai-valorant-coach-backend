import pytest
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app

@pytest.fixture
def api_client(mock_user_repo):
    """Fixture overriding API dependencies with mock repositories."""
    from app.api.dependencies import get_user_repository
    app.dependency_overrides[get_user_repository] = lambda: mock_user_repo
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_api_register_and_login_flow(api_client):
    # 1. Register Account
    reg_payload = {"email": "api_test@example.com", "password": "password123"}
    response = api_client.post("/api/v1/auth/register", json=reg_payload)
    
    assert response.status_code == status.HTTP_201_CREATED
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["email"] == "api_test@example.com"
    assert "request_id" in json_data
    assert "timestamp" in json_data

    # 2. Login OAuth2 Password Request
    login_data = {"username": "api_test@example.com", "password": "password123"}
    login_resp = api_client.post("/api/v1/auth/login", data=login_data)
    assert login_resp.status_code == status.HTTP_200_OK
    login_json = login_resp.json()
    assert login_json["success"] is True
    tokens = login_json["data"]
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    # 3. Retrieve Profile with Header JWT
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    profile_resp = api_client.get("/api/v1/profile", headers=headers)
    assert profile_resp.status_code == status.HTTP_200_OK
    profile_json = profile_resp.json()
    assert profile_json["success"] is True
    assert profile_json["data"]["preferred_agents"] == []

    # 4. Update Profile
    update_payload = {
        "rank": "Ascendant 1",
        "region": "AP",
        "sensitivity": 0.45,
        "mouse_dpi": 1600,
        "preferred_agents": ["Reyna", "Sova"]
    }
    update_resp = api_client.put("/api/v1/profile", json=update_payload, headers=headers)
    assert update_resp.status_code == status.HTTP_200_OK
    update_json = update_resp.json()
    assert update_json["success"] is True
    assert update_json["data"]["rank"] == "Ascendant 1"
    assert update_json["data"]["preferred_agents"] == ["Reyna", "Sova"]

    # 5. Refresh token exchange
    refresh_payload = {"refresh_token": tokens["refresh_token"]}
    refresh_resp = api_client.post("/api/v1/auth/refresh", json=refresh_payload)
    assert refresh_resp.status_code == status.HTTP_200_OK
    refresh_json = refresh_resp.json()
    assert refresh_json["success"] is True
    assert "access_token" in refresh_json["data"]

    # 6. Logout
    logout_payload = {"refresh_token": tokens["refresh_token"]}
    logout_resp = api_client.post("/api/v1/auth/logout", json=logout_payload, headers=headers)
    assert logout_resp.status_code == status.HTTP_200_OK

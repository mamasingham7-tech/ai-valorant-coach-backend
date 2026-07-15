import pytest
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app
from app.shared.security.tokens import create_access_token
from app.modules.users.domain.entities.user import User

@pytest.fixture
def admin_client(mock_user_repo):
    from app.api.dependencies import get_user_repository
    app.dependency_overrides[get_user_repository] = lambda: mock_user_repo
    
    # Pre-populate test admin user
    admin_user = User(
        id="admin-999",
        email="admin@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_verified=True
    )
    admin_user.role = "ADMIN"
    mock_user_repo.users[admin_user.id] = admin_user
    
    # Pre-populate normal user
    normal_user = User(
        id="user-111",
        email="user@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_verified=True
    )
    normal_user.role = "USER"
    mock_user_repo.users[normal_user.id] = normal_user
    
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_admin_system_endpoint(admin_client):
    access_token = create_access_token(data={"sub": "admin-999"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = admin_client.get("/api/v1/admin/system", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["status"] == "optimal"


def test_admin_features_unauthorized(admin_client):
    # Try accessing features toggle using USER role (which lacks manage_feature_flags claim)
    access_token = create_access_token(data={"sub": "user-111"})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = admin_client.get("/api/v1/admin/features", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN

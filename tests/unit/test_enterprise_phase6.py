import pytest
import uuid
from typing import Dict, Any
from fastapi import HTTPException, status
from app.modules.users.domain.entities.user import User
from app.shared.saga.saga import SagaStep, SagaCoordinator
from app.modules.enterprise.domain.entities.permissions import ROLE_PERMISSIONS
from app.modules.enterprise.infrastructure.providers.rbac import (
    has_permission,
    requires_permission,
    APIKeyValidator
)
from app.modules.enterprise.infrastructure.registry.plugin_registry import PluginSDK, PluginRegistry
from app.modules.enterprise.infrastructure.providers.mlops import ModelMLOpsManager
from app.modules.enterprise.infrastructure.providers.feature_flags import FeatureFlagsManager
from app.shared.redis_lock import RedisLock

# --- Saga Tests ---

@pytest.mark.asyncio
async def test_saga_coordinator_success():
    coordinator = SagaCoordinator()
    context = {"val": 10}

    async def step1_act(ctx):
        ctx["val"] += 5
    async def step1_comp(ctx):
        ctx["val"] -= 5

    async def step2_act(ctx):
        ctx["val"] *= 2
    async def step2_comp(ctx):
        ctx["val"] //= 2

    step1 = SagaStep("Add5", step1_act, step1_comp)
    step2 = SagaStep("Mul2", step2_act, step2_comp)

    res = await coordinator.execute([step1, step2], context)
    assert res["val"] == 30
    assert len(coordinator.executed_steps) == 2


@pytest.mark.asyncio
async def test_saga_coordinator_compensation_on_failure():
    coordinator = SagaCoordinator()
    context = {"val": 10}

    async def step1_act(ctx):
        ctx["val"] += 5
    async def step1_comp(ctx):
        ctx["val"] -= 5

    async def step2_act(ctx):
        raise ValueError("Simulated failure step")
    async def step2_comp(ctx):
        pass

    step1 = SagaStep("Add5", step1_act, step1_comp)
    step2 = SagaStep("FailStep", step2_act, step2_comp)

    with pytest.raises(ValueError, match="Simulated failure step"):
        await coordinator.execute([step1, step2], context)

    # Context should be rolled back to original state (15 - 5 = 10)
    assert context["val"] == 10
    assert len(coordinator.executed_steps) == 1


# --- Redis Lock Tests ---

@pytest.mark.asyncio
async def test_redis_lock_acquire_and_release():
    lock = RedisLock("match-ingest-456", ttl_seconds=5)
    acquired = await lock.acquire()
    assert acquired is True
    await lock.release()
    assert lock.acquired is False


# --- RBAC and Decorator Tests ---

def test_rbac_permissions_grid():
    # Verify USER permissions
    assert has_permission("USER", "read_profile") is True
    assert has_permission("USER", "manage_users") is False

    # Verify ADMIN permissions
    assert has_permission("ADMIN", "manage_users") is True
    assert has_permission("ADMIN", "rollout_models") is True


@pytest.mark.asyncio
async def test_requires_permission_decorator_allowed():
    # Helper endpoint-like function
    @requires_permission("manage_users")
    async def admin_only_action(current_user: User):
        return "Allowed"

    user = User(id="user-123", email="a@a.com", hashed_password="pw")
    # Dynamically inject ADMIN role
    user.role = "ADMIN"

    res = await admin_only_action(current_user=user)
    assert res == "Allowed"


@pytest.mark.asyncio
async def test_requires_permission_decorator_blocked():
    @requires_permission("manage_users")
    async def admin_only_action(current_user: User):
        return "Allowed"

    user = User(id="user-123", email="a@a.com", hashed_password="pw")
    user.role = "USER"

    with pytest.raises(HTTPException) as exc_info:
        await admin_only_action(current_user=user)
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


# --- API Key Tests ---

def test_api_key_validator_admin():
    validator = APIKeyValidator()
    claims = validator.validate_key("admin-api-key-999")
    assert claims["role"] == "ADMIN"
    assert "*" in claims["scopes"]


def test_api_key_validator_invalid():
    validator = APIKeyValidator()
    with pytest.raises(HTTPException) as exc_info:
        validator.validate_key("invalid-key")
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


# --- Plugin SDK Tests ---

def test_plugin_sdk_registration():
    registry = PluginRegistry()
    plugin = PluginSDK(name="aim-eval-plugin", version="2.1.0")
    
    registry.register_plugin(plugin)
    assert registry.get_plugin("aim-eval-plugin").version == "2.1.0"
    assert "aim-eval-plugin" in registry.list_plugins()


def test_plugin_sdk_invalid_registration():
    registry = PluginRegistry()
    plugin = PluginSDK(name="", version="")
    with pytest.raises(ValueError, match="Plugin metadata missing"):
        registry.register_plugin(plugin)


# --- MLOps Tests ---

def test_mlops_traffic_split():
    manager = ModelMLOpsManager()
    
    # Assert traffic routing splits traffic deterministically
    model_a = manager.route_traffic("user-777")
    model_b = manager.route_traffic("user-111")
    
    assert model_a in [manager.champion_version, manager.challenger_version]
    assert model_b in [manager.champion_version, manager.challenger_version]


def test_mlops_drift_detection():
    manager = ModelMLOpsManager()
    
    # Assess metrics outputs
    res = manager.evaluate_model_drift("system prompt input", "highly accurate prediction evidence")
    assert res["hallucination_score"] == 0.05
    assert res["drift_detected"] is False

    res_drift = manager.evaluate_model_drift("system prompt input", "poor response description")
    assert res_drift["hallucination_score"] == 0.25
    assert res_drift["drift_detected"] is True


# --- Feature Flags Tests ---

def test_feature_flags_manager_admin():
    manager = FeatureFlagsManager()
    assert manager.is_enabled("dynamic_drills_enabled", role="ADMIN") is True


def test_feature_flags_percent_rollout():
    manager = FeatureFlagsManager()
    
    # Determine enabled status based on deterministic hash calculations
    res_1 = manager.is_enabled("dynamic_drills_enabled", user_id="user-999")
    res_2 = manager.is_enabled("realtime_coaching_enabled", user_id="user-999")
    
    assert res_2 is True
    assert isinstance(res_1, bool)

from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.api.dependencies import get_current_user
from app.modules.users.domain.entities.user import User
from app.modules.enterprise.infrastructure.providers.rbac import requires_permission
from app.modules.enterprise.infrastructure.registry.plugin_registry import plugin_registry
from app.shared.responses.envelope import wrap_response, APIResponseEnvelope

router = APIRouter()

@router.get("/admin/users", response_model=APIResponseEnvelope)
@requires_permission("manage_users")
async def get_admin_users(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Fetches general user profiles for support teams."""
    return wrap_response(
        success=True,
        data=[{
            "user_id": current_user.id,
            "email": current_user.email,
            "role": getattr(current_user, "role", "USER")
        }],
        message="Users list retrieved successfully",
        request_id=request.state.request_id
    )

@router.get("/admin/audit", response_model=APIResponseEnvelope)
@requires_permission("read_audit_logs")
async def get_admin_audit(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Retrieves operational audit trails logs."""
    return wrap_response(
        success=True,
        data=[{"event": "AUTH_LOGIN", "user_id": current_user.id}],
        message="Audit logs fetched",
        request_id=request.state.request_id
    )

@router.get("/admin/plugins", response_model=APIResponseEnvelope)
@requires_permission("register_plugins")
async def get_admin_plugins(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Fetches all registered third-party evaluation plugins."""
    plugins = plugin_registry.list_plugins()
    return wrap_response(
        success=True,
        data=plugins,
        message="Dynamic plugins registry list fetched",
        request_id=request.state.request_id
    )

@router.get("/admin/models", response_model=APIResponseEnvelope)
@requires_permission("manage_models")
async def get_admin_models(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Retrieves metadata properties for the active model configurations."""
    return wrap_response(
        success=True,
        data={"champion": "gpt-4o-v1", "challenger": "gpt-4o-v2"},
        message="ML models configurations retrieved",
        request_id=request.state.request_id
    )

@router.get("/admin/experiments", response_model=APIResponseEnvelope)
@requires_permission("manage_experiments")
async def get_admin_experiments(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Fetches details on currently running A/B experiments rollouts."""
    return wrap_response(
        success=True,
        data={"ab_rollout_groups": ["control", "variant_A"]},
        message="Active experiments rollouts fetched",
        request_id=request.state.request_id
    )

@router.get("/admin/features", response_model=APIResponseEnvelope)
@requires_permission("manage_feature_flags")
async def get_admin_features(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Retrieves details of active dynamic feature toggles."""
    return wrap_response(
        success=True,
        data={"realtime_coaching_enabled": True, "shadow_mlops_enabled": True},
        message="Runtime feature flags list fetched",
        request_id=request.state.request_id
    )

@router.get("/admin/system", response_model=APIResponseEnvelope)
@requires_permission("read_system_stats")
async def get_admin_system(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Fetches system resource statistics and CPU usage telemetry values."""
    return wrap_response(
        success=True,
        data={"status": "optimal", "cpu_load": 12.5, "memory_used_mb": 256},
        message="System telemetry parameters read",
        request_id=request.state.request_id
    )

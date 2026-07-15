from typing import Dict, Any, Optional
import structlog
from structlog.contextvars import get_contextvars
from app.database.database import async_session_maker
from app.modules.users.infrastructure.models.audit_table import AuditLogTable
from app.shared.events.event_bus import event_bus, UserRegistered, UserLoggedIn, ProfileUpdated

logger = structlog.get_logger()

class AuditLogService:
    async def log_action(
        self,
        action: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Asynchronously writes a security action entry to the audit logs."""
        ctx = get_contextvars()
        request_id = ctx.get("request_id")
        correlation_id = ctx.get("correlation_id")
        
        async with async_session_maker() as session:
            try:
                log_entry = AuditLogTable(
                    user_id=user_id,
                    action=action,
                    request_id=request_id,
                    correlation_id=correlation_id,
                    metadata_=metadata or {}
                )
                session.add(log_entry)
                await session.commit()
                
                # Write to stdout/JSON stream under AUDIT namespace
                logger.info(
                    "Security audit log recorded",
                    namespace="audit",
                    action=action,
                    user_id=user_id,
                    request_id=request_id
                )
            except Exception as e:
                logger.exception("Failed to persist security audit record", action=action, error=str(e))

audit_service = AuditLogService()

async def _on_user_registered(event: UserRegistered) -> None:
    await audit_service.log_action(
        action="USER_REGISTERED",
        user_id=event.user_id,
        metadata={"email": event.email}
    )

async def _on_user_logged_in(event: UserLoggedIn) -> None:
    await audit_service.log_action(
        action="USER_LOGGED_IN",
        user_id=event.user_id,
        metadata={"email": event.email}
    )

async def _on_profile_updated(event: ProfileUpdated) -> None:
    await audit_service.log_action(
        action="PROFILE_UPDATED",
        user_id=event.user_id,
        metadata={"updates": event.updates}
    )

def setup_audit_listeners() -> None:
    """Subscribes audit handlers to their respective domain events."""
    event_bus.subscribe(UserRegistered, _on_user_registered)
    event_bus.subscribe(UserLoggedIn, _on_user_logged_in)
    event_bus.subscribe(ProfileUpdated, _on_profile_updated)

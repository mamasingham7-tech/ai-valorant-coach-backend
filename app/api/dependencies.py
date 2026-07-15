from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db_session
from app.modules.users.domain.repositories.user_repository import UserRepository
from app.modules.users.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from app.modules.users.domain.repositories.session_repository import SessionRepository
from app.modules.users.infrastructure.repositories.sqlalchemy_session_repository import SQLAlchemySessionRepository
from app.modules.matches.domain.repositories.match_repository import MatchRepository
from app.modules.matches.infrastructure.repositories.sqlalchemy_match_repository import SQLAlchemyMatchRepository
from app.modules.live_coaching.domain.repositories.live_repository import LiveCoachingRepository
from app.modules.live_coaching.infrastructure.repositories.sqlalchemy_live_repository import SQLAlchemyLiveCoachingRepository
from app.modules.autonomous.domain.repositories.autonomous_repository import AutonomousRepository
from app.modules.autonomous.infrastructure.repositories.sqlalchemy_autonomous_repository import SQLAlchemyAutonomousRepository
from app.modules.federation.domain.repositories.federation_repository import FederationRepository
from app.modules.federation.infrastructure.repositories.sqlalchemy_federation_repository import SQLAlchemyFederationRepository
from app.modules.enterprise.domain.repositories.enterprise_repository import EnterpriseRepository
from app.modules.enterprise.infrastructure.repositories.sqlalchemy_enterprise_repository import SQLAlchemyEnterpriseRepository
from app.shared.security.tokens import decode_token
from app.modules.users.domain.entities.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    """Dependency provider for UserRepository."""
    return SQLAlchemyUserRepository(session)

async def get_session_repository(session: AsyncSession = Depends(get_db_session)) -> SessionRepository:
    """Dependency provider for SessionRepository."""
    return SQLAlchemySessionRepository(session)

async def get_match_repository(session: AsyncSession = Depends(get_db_session)) -> MatchRepository:
    """Dependency provider for MatchRepository."""
    return SQLAlchemyMatchRepository(session)

async def get_live_repository(session: AsyncSession = Depends(get_db_session)) -> LiveCoachingRepository:
    """Dependency provider for LiveCoachingRepository."""
    return SQLAlchemyLiveCoachingRepository(session)

async def get_autonomous_repository(session: AsyncSession = Depends(get_db_session)) -> AutonomousRepository:
    """Dependency provider for AutonomousRepository."""
    return SQLAlchemyAutonomousRepository(session)

async def get_federation_repository(session: AsyncSession = Depends(get_db_session)) -> FederationRepository:
    """Dependency provider for FederationRepository."""
    return SQLAlchemyFederationRepository(session)

async def get_enterprise_repository(session: AsyncSession = Depends(get_db_session)) -> EnterpriseRepository:
    """Dependency provider for EnterpriseRepository."""
    return SQLAlchemyEnterpriseRepository(session)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    """Dependency guard that decodes and validates access tokens."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None or token_type != "access":
            raise credentials_exception
    except ValueError as e:
        raise credentials_exception from e
        
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Guard to ensure the current user is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user account")
    return current_user

def require_role(allowed_roles: list):
    """FastAPI Dependency for Role-Based Access Control."""
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in [r.value for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker

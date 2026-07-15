from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime

from app.modules.users.domain.repositories.session_repository import SessionRepository
from app.modules.users.infrastructure.models.session_table import SessionTable

class SQLAlchemySessionRepository(SessionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_session(self, session_id: str, user_id: str, refresh_token_jti: str, expires_at: datetime, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> None:
        new_session = SessionTable(
            id=session_id,
            user_id=user_id,
            refresh_token_jti=refresh_token_jti,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.session.add(new_session)
        await self.session.commit()

    async def get_session_by_jti(self, jti: str) -> Optional[SessionTable]:
        stmt = select(SessionTable).where(SessionTable.refresh_token_jti == jti)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_active_sessions_for_user(self, user_id: str) -> List[SessionTable]:
        stmt = select(SessionTable).where(
            SessionTable.user_id == user_id,
            SessionTable.is_revoked == False
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def revoke_session(self, session_id: str) -> bool:
        stmt = update(SessionTable).where(SessionTable.id == session_id).values(is_revoked=True)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def revoke_all_user_sessions(self, user_id: str) -> None:
        stmt = update(SessionTable).where(SessionTable.user_id == user_id).values(is_revoked=True)
        await self.session.execute(stmt)
        await self.session.commit()

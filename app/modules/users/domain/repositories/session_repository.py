from typing import Optional, List
from abc import ABC, abstractmethod
from datetime import datetime

class SessionRepository(ABC):
    @abstractmethod
    async def create_session(self, session_id: str, user_id: str, refresh_token_jti: str, expires_at: datetime, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> None:
        pass

    @abstractmethod
    async def get_session_by_jti(self, jti: str):
        pass

    @abstractmethod
    async def get_active_sessions_for_user(self, user_id: str):
        pass

    @abstractmethod
    async def revoke_session(self, session_id: str) -> bool:
        pass

    @abstractmethod
    async def revoke_all_user_sessions(self, user_id: str) -> None:
        pass

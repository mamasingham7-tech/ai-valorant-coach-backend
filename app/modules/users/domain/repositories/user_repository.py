from abc import ABC, abstractmethod
from typing import Optional
from app.modules.users.domain.entities.user import User, PlayerProfile

class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Retrieve a user by their unique identifier."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email address."""
        pass

    @abstractmethod
    async def save(self, user: User) -> User:
        """Create or insert a new user in the persistent store."""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user in the persistent store."""
        pass

    @abstractmethod
    async def get_profile(self, user_id: str) -> Optional[PlayerProfile]:
        """Retrieve a player profile by user ID."""
        pass

    @abstractmethod
    async def save_profile(self, profile: PlayerProfile) -> PlayerProfile:
        """Save (create or update) a player profile."""
        pass

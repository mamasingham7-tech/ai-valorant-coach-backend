import pytest
from typing import List, Optional
from app.modules.users.domain.entities.user import User, PlayerProfile
from app.modules.users.domain.repositories.user_repository import UserRepository
from app.modules.matches.domain.entities.match import Match, GameplayEvent
from app.modules.matches.domain.repositories.match_repository import MatchRepository

class MockUserRepository(UserRepository):
    def __init__(self):
        self.users = {}
        self.profiles = {}

    async def get_by_id(self, user_id: str):
        return self.users.get(user_id)

    async def get_by_email(self, email: str):
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    async def save(self, user: User):
        self.users[user.id] = user
        return user

    async def update(self, user: User):
        self.users[user.id] = user
        return user

    async def get_profile(self, user_id: str):
        return self.profiles.get(user_id)

    async def save_profile(self, profile: PlayerProfile):
        self.profiles[profile.user_id] = profile
        return profile

class MockMatchRepository(MatchRepository):
    def __init__(self):
        self.matches = {}
        self.events = {}

    async def get_match(self, match_id: str) -> Optional[Match]:
        return self.matches.get(match_id)

    async def save_match(self, match: Match) -> Match:
        self.matches[match.id] = match
        return match

    async def get_player_matches(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Match]:
        res = []
        for m in self.matches.values():
            for p in m.players:
                if p.user_id == user_id:
                    res.append(m)
                    break
        res.sort(key=lambda x: x.match_start_time, reverse=True)
        return res[offset : offset + limit]

    async def save_gameplay_events(self, events: List[GameplayEvent]) -> None:
        for e in events:
            if e.match_id not in self.events:
                self.events[e.match_id] = []
            self.events[e.match_id].append(e)

    async def get_gameplay_events(self, match_id: str) -> List[GameplayEvent]:
        return self.events.get(match_id, [])

@pytest.fixture
def mock_user_repo() -> UserRepository:
    """Fixture returning an in-memory mock implementation of UserRepository."""
    return MockUserRepository()

@pytest.fixture
def mock_match_repo() -> MatchRepository:
    """Fixture returning an in-memory mock implementation of MatchRepository."""
    return MockMatchRepository()

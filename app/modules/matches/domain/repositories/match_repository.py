from abc import ABC, abstractmethod
from typing import Optional, List
from app.modules.matches.domain.entities.match import Match, GameplayEvent

class MatchRepository(ABC):
    @abstractmethod
    async def get_match(self, match_id: str) -> Optional[Match]:
        """Retrieve a match by its unique identifier along with players and rounds."""
        pass

    @abstractmethod
    async def save_match(self, match: Match) -> Match:
        """Persist a complete match structure (includes Match, MatchPlayers, and Rounds)."""
        pass

    @abstractmethod
    async def get_player_matches(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Match]:
        """Retrieve match summaries for a specific player with support for pagination."""
        pass

    @abstractmethod
    async def save_gameplay_events(self, events: List[GameplayEvent]) -> None:
        """Batch persist fine-grained telemetry events (partitioned)."""
        pass

    @abstractmethod
    async def get_gameplay_events(self, match_id: str) -> List[GameplayEvent]:
        """Retrieve telemetry events for a specific match."""
        pass

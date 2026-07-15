from abc import ABC, abstractmethod
from typing import Optional, List
from app.modules.player_portal.domain.entities import RiotAccount, ValorantRank, MatchSummary

class IValorantProvider(ABC):
    """Abstract provider interface. All Valorant data providers must implement this.
    
    This abstraction ensures the rest of the application never depends on a specific
    data source. Providers can be swapped without changing business logic.
    """

    @abstractmethod
    async def get_account(self, game_name: str, tag_line: str) -> Optional[RiotAccount]:
        """Look up a Riot account by GameName and TagLine. Returns None if not found."""
        ...

    @abstractmethod
    async def get_rank(self, game_name: str, tag_line: str, region: str) -> Optional[ValorantRank]:
        """Fetch current competitive rank, RR, and peak rank information."""
        ...

    @abstractmethod
    async def get_match_history(
        self, game_name: str, tag_line: str, region: str,
        mode: str = "competitive", size: int = 20
    ) -> List[MatchSummary]:
        """Fetch recent match history for a player."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique identifier for this provider."""
        ...

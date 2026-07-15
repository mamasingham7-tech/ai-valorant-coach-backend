import random
from datetime import datetime
from typing import Optional, List
from app.modules.player_portal.application.providers.base import IValorantProvider
from app.modules.player_portal.domain.entities import RiotAccount, ValorantRank, MatchSummary

MOCK_MAPS   = ["Haven", "Bind", "Breeze", "Icebox", "Split", "Fracture", "Lotus", "Pearl", "Sunset", "Abyss"]
MOCK_AGENTS = ["Jett", "Reyna", "Chamber", "Killjoy", "Sage", "Omen", "Brimstone", "Neon", "Yoru", "Iso"]
MOCK_RANKS  = ["Iron 1", "Bronze 2", "Silver 3", "Gold 1", "Platinum 2", "Diamond 1", "Immortal 2", "Radiant"]

class MockProvider(IValorantProvider):
    """Development mock provider. Returns realistic randomised data.
    
    Used when:
    - USE_MOCK_PROVIDER=true in .env
    - No real API keys are configured
    - Development / testing / demo purposes
    
    Does NOT make any external HTTP requests.
    """

    @property
    def provider_name(self) -> str:
        return "mock"

    async def get_account(self, game_name: str, tag_line: str) -> Optional[RiotAccount]:
        """Always succeeds — returns a plausible mock account."""
        return RiotAccount(
            id="",
            user_id="",
            game_name=game_name,
            tag_line=tag_line,
            puuid=f"mock-puuid-{game_name.lower()}-{tag_line.lower()}",
            region="na",
            account_level=random.randint(50, 350),
            is_verified=True,
            provider=self.provider_name,
        )

    async def get_rank(self, game_name: str, tag_line: str, region: str) -> Optional[ValorantRank]:
        tier = random.choice(MOCK_RANKS)
        return ValorantRank(
            tier=tier,
            tier_name=tier,
            rr=random.randint(0, 99),
            peak_tier="Radiant" if random.random() > 0.7 else "Immortal 3",
            elo=random.randint(1600, 2500),
            leaderboard_rank=random.randint(1, 500) if tier == "Radiant" else None,
        )

    async def get_match_history(
        self, game_name: str, tag_line: str, region: str,
        mode: str = "competitive", size: int = 20
    ) -> List[MatchSummary]:
        matches = []
        for i in range(min(size, 15)):
            won = random.random() > 0.42
            my_r  = 13 if won else random.randint(5, 12)
            opp_r = random.randint(5, 11) if won else 13
            k = random.randint(8, 32)
            d = random.randint(6, 22)
            matches.append(MatchSummary(
                match_id=f"mock-{i}-{game_name.lower()}",
                map_name=random.choice(MOCK_MAPS),
                game_mode=mode,
                started_at=datetime.utcnow().isoformat(),
                duration=random.randint(25 * 60, 52 * 60),
                result="WIN" if won else "LOSS",
                agent=random.choice(MOCK_AGENTS),
                kills=k,
                deaths=d,
                assists=random.randint(2, 12),
                acs=round(random.uniform(150, 345), 1),
                hs_percent=round(random.uniform(14, 40), 1),
                adr=round(random.uniform(100, 230), 1),
                score=f"{my_r}-{opp_r}",
                rr_change=random.randint(5, 30) if won else random.randint(-25, -5),
            ))
        return matches

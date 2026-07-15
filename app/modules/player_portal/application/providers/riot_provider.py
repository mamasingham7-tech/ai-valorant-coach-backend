import httpx
import structlog
from typing import Optional, List
from app.modules.player_portal.application.providers.base import IValorantProvider
from app.modules.player_portal.domain.entities import RiotAccount, ValorantRank, MatchSummary

logger = structlog.get_logger()

# Official Riot routing map: region -> routing cluster
RIOT_REGION_MAP = {
    "na": "americas", "latam": "americas", "br": "americas",
    "eu": "europe",
    "ap": "asia", "kr": "asia",
}

class RiotOfficialProvider(IValorantProvider):
    """Secondary provider using the official Riot Games Developer API.
    
    REQUIREMENTS:
    - Requires an approved Riot Developer API key in RIOT_API_KEY env var.
    - Development keys are rate-limited (100 req/2min, 20 req/1s).
    - Production keys require application to Riot Developer Portal.
    
    NOTE: Riot RSO (Sign-in with Riot OAuth) is NOT publicly available.
    It is exclusive to official Riot Game partners only.
    This provider uses server-to-server API calls only.
    
    Docs: https://developer.riotgames.com/apis
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"X-Riot-Token": self.api_key}

    @property
    def provider_name(self) -> str:
        return "riot_official"

    def _routing(self, region: str) -> str:
        return RIOT_REGION_MAP.get(region.lower(), "americas")

    async def get_account(self, game_name: str, tag_line: str) -> Optional[RiotAccount]:
        """GET /riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"""
        url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=self.headers)
                if resp.status_code != 200:
                    logger.warning("Riot API account lookup failed", status=resp.status_code)
                    return None
                data = resp.json()
                return RiotAccount(
                    id="",
                    user_id="",
                    game_name=game_name,
                    tag_line=tag_line,
                    puuid=data.get("puuid", ""),
                    region="na",   # Region is not returned by this endpoint
                    account_level=0,
                    is_verified=True,
                    provider=self.provider_name,
                )
        except Exception as e:
            logger.error("RiotAPI get_account error", error=str(e))
            return None

    async def get_rank(self, game_name: str, tag_line: str, region: str) -> Optional[ValorantRank]:
        """The official Riot API does NOT expose individual rank by game name.
        VAL-RANKED-V1 only provides leaderboards. Rank lookup requires PUUID
        from match data, which is not a simple single endpoint.
        Returns None — recommend using HenrikDev for rank data."""
        logger.info("RiotOfficialProvider: rank by game name not supported via official API")
        return None

    async def get_match_history(
        self, game_name: str, tag_line: str, region: str,
        mode: str = "competitive", size: int = 20
    ) -> List[MatchSummary]:
        """Official flow: get PUUID first, then fetch matchlist by PUUID."""
        account = await self.get_account(game_name, tag_line)
        if not account or not account.puuid:
            return []
        routing = self._routing(region)
        url = f"https://{routing}.api.riotgames.com/val/match/v1/matchlists/by-puuid/{account.puuid}"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, headers=self.headers)
                if resp.status_code != 200:
                    return []
                # NOTE: This endpoint only returns match IDs, not full match data.
                # Full data requires one GET per match (heavy rate-limiting).
                # HenrikDev provides full data in a single call — strongly preferred.
                logger.info("Riot API matchlist returned", count=len(resp.json().get("history", [])))
                return []
        except Exception as e:
            logger.error("RiotAPI match history error", error=str(e))
            return []

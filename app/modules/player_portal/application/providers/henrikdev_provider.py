import httpx
import structlog
from typing import Optional, List
from app.modules.player_portal.application.providers.base import IValorantProvider
from app.modules.player_portal.domain.entities import RiotAccount, ValorantRank, MatchSummary

logger = structlog.get_logger()
BASE_URL = "https://api.henrikdev.xyz"

class HenrikDevProvider(IValorantProvider):
    """Primary Valorant data provider using the HenrikDev community API.

    Requires a free API key from https://app.henrikdev.xyz
    (free registration, instant key).

    Docs: https://docs.henrikdev.xyz/valorant/general
    """

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key
        if not api_key:
            logger.warning(
                "HenrikDevProvider: No HENRIK_API_KEY set. "
                "Get a free key at https://app.henrikdev.xyz — "
                "or set USE_MOCK_PROVIDER=true in .env for development."
            )

    def _map_region(self, region: str) -> str:
        """Map user-friendly regions to official API shards."""
        region_map = {
            "in": "ap",  # India uses AP shard
            "me": "eu",  # Middle East uses EU shard
            "latam": "na", # Latam might be its own or NA depending on API version, but usually latam works.
        }
        return region_map.get(region.lower(), region.lower())

    @property
    def provider_name(self) -> str:
        return "henrikdev"

    def _headers(self) -> dict:
        h = {"Accept": "application/json"}
        if self._api_key:
            h["Authorization"] = self._api_key
        return h

    async def get_account(self, game_name: str, tag_line: str) -> Optional[RiotAccount]:
        """GET /valorant/v1/account/{name}/{tag}"""
        url = f"{BASE_URL}/valorant/v1/account/{game_name}/{tag_line}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=self._headers())
                if resp.status_code == 401:
                    logger.error(
                        "HenrikDev API key missing or invalid. "
                        "Get a free key at https://app.henrikdev.xyz"
                    )
                    return None
                if resp.status_code == 404:
                    logger.info("Riot account not found", game_name=game_name, tag=tag_line)
                    return None
                if resp.status_code != 200:
                    logger.warning("HenrikDev account lookup failed",
                                   status=resp.status_code,
                                   game_name=game_name, tag=tag_line,
                                   body=resp.text[:200])
                    return None
                data = resp.json().get("data", {})
                return RiotAccount(
                    id="",
                    user_id="",
                    game_name=data.get("name", game_name),
                    tag_line=data.get("tag", tag_line),
                    puuid=data.get("puuid", ""),
                    region=data.get("region", "na").lower(),
                    account_level=data.get("account_level", 0),
                    is_verified=True,
                    provider=self.provider_name,
                )
        except Exception as e:
            logger.error("HenrikDev get_account error", error=str(e))
            return None

    async def get_rank(self, game_name: str, tag_line: str, region: str) -> Optional[ValorantRank]:
        """GET /valorant/v2/mmr/{region}/{name}/{tag}"""
        mapped_region = self._map_region(region)
        url = f"{BASE_URL}/valorant/v2/mmr/{mapped_region}/{game_name}/{tag_line}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=self._headers())
                if resp.status_code != 200:
                    return None
                data = resp.json().get("data", {})
                current = data.get("current_data", {})
                highest = data.get("highest_rank", {})
                return ValorantRank(
                    tier=current.get("currenttierpatched", "Unranked"),
                    tier_name=current.get("currenttierpatched", "Unranked"),
                    rr=current.get("ranking_in_tier", 0),
                    peak_tier=highest.get("patched_tier"),
                    elo=current.get("elo"),
                    leaderboard_rank=None,
                )
        except Exception as e:
            logger.error("HenrikDev get_rank error", error=str(e))
            return None

    async def get_match_history(
        self, game_name: str, tag_line: str, region: str,
        mode: str = "competitive", size: int = 20
    ) -> List[MatchSummary]:
        """GET /valorant/v3/matches/{region}/{name}/{tag}"""
        mapped_region = self._map_region(region)
        url = f"{BASE_URL}/valorant/v3/matches/{mapped_region}/{game_name}/{tag_line}?mode={mode}&size={size}"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, headers=self._headers())
                if resp.status_code != 200:
                    return []
                matches_raw = resp.json().get("data", [])
                results = []
                for m in matches_raw:
                    meta = m.get("metadata", {})
                    all_players = m.get("players", {}).get("all_players", [])

                    player = next(
                        (p for p in all_players
                         if p.get("name", "").lower() == game_name.lower()
                         and p.get("tag", "").lower() == tag_line.lower()),
                        None
                    )
                    if not player:
                        continue

                    stats = player.get("stats", {})
                    team_color = player.get("team", "Red").lower()
                    teams = m.get("teams", {})
                    my_team = teams.get(team_color, {})
                    opp_color = "blue" if team_color == "red" else "red"
                    opp_team = teams.get(opp_color, {})
                    won = my_team.get("has_won", False)
                    my_rounds = my_team.get("rounds_won", 0)
                    opp_rounds = opp_team.get("rounds_won", 0)
                    rounds_played = max(meta.get("rounds_played", 1), 1)
                    head_shots = stats.get("headshots", 0)
                    body_shots = stats.get("bodyshots", 0)
                    leg_shots = stats.get("legshots", 0)
                    total_shots = max(head_shots + body_shots + leg_shots, 1)

                    results.append(MatchSummary(
                        match_id=meta.get("matchid", ""),
                        map_name=meta.get("map", "Unknown"),
                        game_mode=meta.get("mode", mode),
                        started_at=str(meta.get("game_start", "")),
                        duration=meta.get("game_length", 0),
                        result="WIN" if won else "LOSS",
                        agent=player.get("character", "Unknown"),
                        kills=stats.get("kills", 0),
                        deaths=stats.get("deaths", 0),
                        assists=stats.get("assists", 0),
                        acs=round(stats.get("score", 0) / rounds_played, 1),
                        hs_percent=round(head_shots / max(total_shots, 1) * 100, 1),
                        adr=round(player.get("damage_made", 0) / rounds_played, 1),
                        score=f"{my_rounds}-{opp_rounds}",
                        rr_change=None,
                    ))
                return results
        except Exception as e:
            logger.error("HenrikDev get_match_history error", error=str(e))
            return []

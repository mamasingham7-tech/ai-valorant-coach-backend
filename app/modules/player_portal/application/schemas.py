from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any

class RiotIDLinkRequest(BaseModel):
    riot_id: str = Field(..., description="Riot ID in format GameName#TAG — e.g. TenZ#NA1")

    @field_validator("riot_id")
    @classmethod
    def validate_riot_id(cls, v: str) -> str:
        v = v.strip()
        if "#" not in v:
            raise ValueError("Riot ID must be in format GameName#TAG (e.g. TenZ#NA1)")
        parts = v.split("#", 1)
        if len(parts[0]) < 1 or len(parts[0]) > 16:
            raise ValueError("Game name must be 1-16 characters")
        if len(parts[1]) < 2 or len(parts[1]) > 5:
            raise ValueError("Tag must be 2-5 characters")
        return v

class RiotAccountResponse(BaseModel):
    id: str
    game_name: str
    tag_line: str
    riot_id: str
    puuid: str
    region: str
    account_level: int
    is_verified: bool
    last_sync: Optional[str] = None
    provider: str

class RankResponse(BaseModel):
    tier: str
    tier_name: str
    rr: int
    peak_tier: Optional[str] = None
    elo: Optional[int] = None
    leaderboard_rank: Optional[int] = None

class MatchSummaryResponse(BaseModel):
    match_id: str
    map_name: str
    game_mode: str
    started_at: str
    duration: int
    result: str
    agent: str
    kills: int
    deaths: int
    assists: int
    acs: float
    hs_percent: float
    adr: float
    score: str
    rr_change: Optional[int] = None

class SyncStatusResponse(BaseModel):
    provider: str
    account_linked: bool
    last_sync: Optional[str] = None
    riot_id: Optional[str] = None
    region: Optional[str] = None

class PlayerStatsResponse(BaseModel):
    riot_id: str
    region: str
    account_level: int
    rank: Optional[RankResponse] = None
    recent_matches: List[MatchSummaryResponse] = []
    win_rate: Optional[float] = None
    avg_acs: Optional[float] = None
    avg_hs: Optional[float] = None
    avg_kda: Optional[float] = None

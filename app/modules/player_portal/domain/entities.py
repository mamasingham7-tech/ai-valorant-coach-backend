from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class RiotAccount:
    id: str
    user_id: str
    game_name: str
    tag_line: str
    puuid: str
    region: str
    account_level: int
    is_verified: bool = False
    last_sync: Optional[datetime] = None
    provider: str = "henrikdev"
    created_at: Optional[datetime] = None

    @property
    def riot_id(self) -> str:
        return f"{self.game_name}#{self.tag_line}"

@dataclass
class ValorantRank:
    tier: str
    tier_name: str
    rr: int
    peak_tier: Optional[str] = None
    leaderboard_rank: Optional[int] = None
    elo: Optional[int] = None

@dataclass
class MatchSummary:
    match_id: str
    map_name: str
    game_mode: str
    started_at: str
    duration: int
    result: str          # WIN / LOSS / DRAW
    agent: str
    kills: int
    deaths: int
    assists: int
    acs: float
    hs_percent: float
    adr: float
    score: str           # "13-8"
    rr_change: Optional[int] = None

@dataclass
class SyncJob:
    id: str
    user_id: str
    riot_account_id: str
    status: str          # pending / running / done / failed
    provider: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    matches_synced: int = 0
    error_message: Optional[str] = None

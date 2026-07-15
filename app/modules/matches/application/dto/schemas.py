from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

class MatchPlayerIngest(BaseModel):
    user_id: str
    agent_name: str
    team_id: str
    kills: int = Field(default=0, ge=0)
    deaths: int = Field(default=0, ge=0)
    assists: int = Field(default=0, ge=0)
    score: int = Field(default=0, ge=0)
    damage_dealt: int = Field(default=0, ge=0)
    rounds_played: int = Field(default=0, ge=0)
    headshots: int = Field(default=0, ge=0)
    shots_fired: int = Field(default=0, ge=0)
    shots_hit: int = Field(default=0, ge=0)

class MatchRoundIngest(BaseModel):
    round_number: int = Field(..., ge=1)
    winning_team: str
    win_reason: str
    spike_planter: Optional[str] = None
    spike_defuser: Optional[str] = None

class MatchEventIngest(BaseModel):
    id: str
    round_number: int = Field(..., ge=0)
    event_type: str
    timestamp_ms: int = Field(..., ge=0)
    x_coord: Optional[float] = None
    y_coord: Optional[float] = None
    z_coord: Optional[float] = None
    metadata: Dict[str, Any] = {}

class IngestMatchRequest(BaseModel):
    match_id: str
    map_name: str
    game_mode: str
    match_start_time: datetime
    duration_ms: int
    players: List[MatchPlayerIngest]
    rounds: List[MatchRoundIngest]
    events: List[MatchEventIngest] = []

# Response Schemas
class MatchPlayerResponse(BaseModel):
    user_id: str
    agent_name: str
    team_id: str
    kills: int
    deaths: int
    assists: int
    score: int
    damage_dealt: int
    rounds_played: int
    headshots: int

class MatchRoundResponse(BaseModel):
    round_number: int
    winning_team: str
    win_reason: str
    spike_planter: Optional[str]
    spike_defuser: Optional[str]

class MatchResponse(BaseModel):
    id: str
    map_name: str
    game_mode: str
    match_start_time: datetime
    duration_ms: int
    players: List[MatchPlayerResponse]
    rounds: List[MatchRoundResponse]

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any

@dataclass
class GameplayEvent:
    id: str
    match_id: str
    round_number: int
    event_type: str
    timestamp_ms: int
    x_coord: Optional[float] = None
    y_coord: Optional[float] = None
    z_coord: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Round:
    match_id: str
    round_number: int
    winning_team: str
    win_reason: str
    spike_planter: Optional[str] = None
    spike_defuser: Optional[str] = None

@dataclass
class MatchPlayer:
    match_id: str
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
    shots_fired: int
    shots_hit: int

@dataclass
class Match:
    id: str
    map_name: str
    game_mode: str
    match_start_time: datetime
    duration_ms: int
    players: List[MatchPlayer] = field(default_factory=list)
    rounds: List[Round] = field(default_factory=list)

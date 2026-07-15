from app.modules.matches.domain.entities.match import Match, MatchPlayer, Round, GameplayEvent
from app.modules.matches.domain.repositories.match_repository import MatchRepository
from app.modules.matches.application.dto.schemas import IngestMatchRequest
from app.shared.events.event_bus import event_bus, Event

class MatchIngested(Event):
    def __init__(self, match_id: str, map_name: str, timestamp_ms: int = None):
        super().__init__(timestamp_ms)
        self.match_id = match_id
        self.map_name = map_name

class IngestMatchUseCase:
    def __init__(self, match_repo: MatchRepository):
        self.match_repo = match_repo

    async def execute(self, request: IngestMatchRequest) -> Match:
        existing = await self.match_repo.get_match(request.match_id)
        if existing:
            return existing

        # Convert DTO to Domain Match
        players = [
            MatchPlayer(
                match_id=request.match_id,
                user_id=p.user_id,
                agent_name=p.agent_name,
                team_id=p.team_id,
                kills=p.kills,
                deaths=p.deaths,
                assists=p.assists,
                score=p.score,
                damage_dealt=p.damage_dealt,
                rounds_played=p.rounds_played,
                headshots=p.headshots,
                shots_fired=p.shots_fired,
                shots_hit=p.shots_hit
            ) for p in request.players
        ]

        rounds = [
            Round(
                match_id=request.match_id,
                round_number=r.round_number,
                winning_team=r.winning_team,
                win_reason=r.win_reason,
                spike_planter=r.spike_planter,
                spike_defuser=r.spike_defuser
            ) for r in request.rounds
        ]

        match_domain = Match(
            id=request.match_id,
            map_name=request.map_name,
            game_mode=request.game_mode,
            match_start_time=request.match_start_time,
            duration_ms=request.duration_ms,
            players=players,
            rounds=rounds
        )

        # Save match stats aggregates
        await self.match_repo.save_match(match_domain)

        # Map and save telemetry events
        if request.events:
            events = [
                GameplayEvent(
                    id=e.id,
                    match_id=request.match_id,
                    round_number=e.round_number,
                    event_type=e.event_type,
                    timestamp_ms=e.timestamp_ms,
                    x_coord=e.x_coord,
                    y_coord=e.y_coord,
                    z_coord=e.z_coord,
                    metadata=e.metadata
                ) for e in request.events
            ]
            await self.match_repo.save_gameplay_events(events)

        # Publish event
        await event_bus.publish(
            MatchIngested(match_id=request.match_id, map_name=request.map_name)
        )
        
        return match_domain

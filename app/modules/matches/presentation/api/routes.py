from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.api.dependencies import get_match_repository, get_current_user
from app.modules.matches.domain.repositories.match_repository import MatchRepository
from app.modules.matches.application.dto.schemas import IngestMatchRequest, MatchResponse, MatchPlayerResponse, MatchRoundResponse
from app.modules.matches.application.use_cases.ingest_match import IngestMatchUseCase
from app.shared.responses.envelope import wrap_response, APIResponseEnvelope
from app.modules.users.domain.entities.user import User

router = APIRouter()

@router.post("/matches/ingest", response_model=APIResponseEnvelope, status_code=status.HTTP_201_CREATED)
async def ingest_match(
    request: Request,
    ingest_req: IngestMatchRequest,
    current_user: User = Depends(get_current_user),
    match_repo: MatchRepository = Depends(get_match_repository)
):
    """Ingest match telemetry aggregates and event timeline logs."""
    use_case = IngestMatchUseCase(match_repo)
    try:
        match = await use_case.execute(ingest_req)
        # Parse match domain to schema response
        res_data = MatchResponse(
            id=match.id,
            map_name=match.map_name,
            game_mode=match.game_mode,
            match_start_time=match.match_start_time,
            duration_ms=match.duration_ms,
            players=[
                MatchPlayerResponse(
                    user_id=p.user_id,
                    agent_name=p.agent_name,
                    team_id=p.team_id,
                    kills=p.kills,
                    deaths=p.deaths,
                    assists=p.assists,
                    score=p.score,
                    damage_dealt=p.damage_dealt,
                    rounds_played=p.rounds_played,
                    headshots=p.headshots
                ) for p in match.players
            ],
            rounds=[
                MatchRoundResponse(
                    round_number=r.round_number,
                    winning_team=r.winning_team,
                    win_reason=r.win_reason,
                    spike_planter=r.spike_planter,
                    spike_defuser=r.spike_defuser
                ) for r in match.rounds
            ]
        )
        return wrap_response(
            success=True,
            data=res_data,
            message="Match ingested successfully",
            request_id=request.state.request_id,
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/matches/{match_id}", response_model=APIResponseEnvelope)
async def get_match(
    request: Request,
    match_id: str,
    current_user: User = Depends(get_current_user),
    match_repo: MatchRepository = Depends(get_match_repository)
):
    """Retrieve detailed game metrics for a specific match ID."""
    match = await match_repo.get_match(match_id)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
        
    res_data = MatchResponse(
        id=match.id,
        map_name=match.map_name,
        game_mode=match.game_mode,
        match_start_time=match.match_start_time,
        duration_ms=match.duration_ms,
        players=[
            MatchPlayerResponse(
                user_id=p.user_id,
                agent_name=p.agent_name,
                team_id=p.team_id,
                kills=p.kills,
                deaths=p.deaths,
                assists=p.assists,
                score=p.score,
                damage_dealt=p.damage_dealt,
                rounds_played=p.rounds_played,
                headshots=p.headshots
            ) for p in match.players
        ],
        rounds=[
            MatchRoundResponse(
                round_number=r.round_number,
                winning_team=r.winning_team,
                win_reason=r.win_reason,
                spike_planter=r.spike_planter,
                spike_defuser=r.spike_defuser
            ) for r in match.rounds
        ]
    )
    return wrap_response(
        success=True,
        data=res_data,
        message="Match retrieved successfully",
        request_id=request.state.request_id
    )

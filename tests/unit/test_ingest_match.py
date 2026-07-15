import pytest
from datetime import datetime, timezone
from app.modules.matches.application.dto.schemas import IngestMatchRequest, MatchPlayerIngest, MatchRoundIngest, MatchEventIngest
from app.modules.matches.application.use_cases.ingest_match import IngestMatchUseCase

@pytest.mark.asyncio
async def test_ingest_match_success(mock_match_repo):
    use_case = IngestMatchUseCase(mock_match_repo)
    
    # Formulate dummy ingest request
    request = IngestMatchRequest(
        match_id="match-uuid-111",
        map_name="Bind",
        game_mode="Competitive",
        match_start_time=datetime.now(timezone.utc),
        duration_ms=2400000,
        players=[
            MatchPlayerIngest(
                user_id="user-uuid-1",
                agent_name="Jett",
                team_id="blue",
                kills=25,
                deaths=15,
                assists=5,
                score=7000,
                damage_dealt=4500,
                rounds_played=24,
                headshots=12,
                shots_fired=120,
                shots_hit=45
            )
        ],
        rounds=[
            MatchRoundIngest(
                round_number=1,
                winning_team="blue",
                win_reason="ELIMINATION"
            )
        ],
        events=[
            MatchEventIngest(
                id="event-1",
                round_number=1,
                event_type="KILL",
                timestamp_ms=45000,
                x_coord=1200.5,
                y_coord=2400.3,
                z_coord=50.2,
                metadata={"weapon": "Vandal", "victim": "user-uuid-2"}
            )
        ]
    )
    
    # 1. Execute Use Case
    match = await use_case.execute(request)
    assert match.id == "match-uuid-111"
    assert match.map_name == "Bind"
    assert len(match.players) == 1
    assert match.players[0].agent_name == "Jett"
    assert len(match.rounds) == 1
    assert match.rounds[0].winning_team == "blue"
    
    # Verify events saved
    events = await mock_match_repo.get_gameplay_events("match-uuid-111")
    assert len(events) == 1
    assert events[0].event_type == "KILL"
    assert events[0].metadata["weapon"] == "Vandal"

    # 2. Re-ingesting existing match returns existing domain object without duplicate write errors
    match_dup = await use_case.execute(request)
    assert match_dup.id == match.id

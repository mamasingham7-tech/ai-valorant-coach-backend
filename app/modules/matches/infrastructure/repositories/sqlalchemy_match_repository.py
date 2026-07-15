from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.modules.matches.domain.entities.match import Match, MatchPlayer, Round, GameplayEvent
from app.modules.matches.domain.repositories.match_repository import MatchRepository
from app.modules.matches.infrastructure.models.match import MatchTable
from app.modules.matches.infrastructure.models.player_stats import MatchPlayerTable
from app.modules.matches.infrastructure.models.round import RoundTable
from app.modules.matches.infrastructure.models.event import GameplayEventTable

class SQLAlchemyMatchRepository(MatchRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain_match(self, m_table: MatchTable) -> Match:
        return Match(
            id=m_table.id,
            map_name=m_table.map_name,
            game_mode=m_table.game_mode,
            match_start_time=m_table.match_start_time,
            duration_ms=m_table.duration_ms,
            players=[self._to_domain_player(p) for p in m_table.players],
            rounds=[self._to_domain_round(r) for r in m_table.rounds]
        )

    def _to_domain_player(self, p_table: MatchPlayerTable) -> MatchPlayer:
        return MatchPlayer(
            match_id=p_table.match_id,
            user_id=p_table.user_id,
            agent_name=p_table.agent_name,
            team_id=p_table.team_id,
            kills=p_table.kills,
            deaths=p_table.deaths,
            assists=p_table.assists,
            score=p_table.score,
            damage_dealt=p_table.damage_dealt,
            rounds_played=p_table.rounds_played,
            headshots=p_table.headshots,
            shots_fired=p_table.shots_fired,
            shots_hit=p_table.shots_hit
        )

    def _to_domain_round(self, r_table: RoundTable) -> Round:
        return Round(
            match_id=r_table.match_id,
            round_number=r_table.round_number,
            winning_team=r_table.winning_team,
            win_reason=r_table.win_reason,
            spike_planter=r_table.spike_planter,
            spike_defuser=r_table.spike_defuser
        )

    def _to_domain_event(self, e_table: GameplayEventTable) -> GameplayEvent:
        return GameplayEvent(
            id=e_table.id,
            match_id=e_table.match_id,
            round_number=e_table.round_number,
            event_type=e_table.event_type,
            timestamp_ms=e_table.timestamp_ms,
            x_coord=e_table.x_coord,
            y_coord=e_table.y_coord,
            z_coord=e_table.z_coord,
            metadata=e_table.metadata_
        )

    async def get_match(self, match_id: str) -> Optional[Match]:
        stmt = (
            select(MatchTable)
            .where(MatchTable.id == match_id)
            .options(selectinload(MatchTable.players), selectinload(MatchTable.rounds))
        )
        res = await self.session.execute(stmt)
        m_table = res.scalar_one_or_none()
        if not m_table:
            return None
        return self._to_domain_match(m_table)

    async def save_match(self, match: Match) -> Match:
        m_table = MatchTable(
            id=match.id,
            map_name=match.map_name,
            game_mode=match.game_mode,
            match_start_time=match.match_start_time,
            duration_ms=match.duration_ms
        )
        self.session.add(m_table)
        await self.session.flush()

        for player in match.players:
            p_table = MatchPlayerTable(
                match_id=player.match_id,
                user_id=player.user_id,
                agent_name=player.agent_name,
                team_id=player.team_id,
                kills=player.kills,
                deaths=player.deaths,
                assists=player.assists,
                score=player.score,
                damage_dealt=player.damage_dealt,
                rounds_played=player.rounds_played,
                headshots=player.headshots,
                shots_fired=player.shots_fired,
                shots_hit=player.shots_hit
            )
            self.session.add(p_table)

        for round_obj in match.rounds:
            r_table = RoundTable(
                match_id=round_obj.match_id,
                round_number=round_obj.round_number,
                winning_team=round_obj.winning_team,
                win_reason=round_obj.win_reason,
                spike_planter=round_obj.spike_planter,
                spike_defuser=round_obj.spike_defuser
            )
            self.session.add(r_table)

        await self.session.flush()
        return match

    async def get_player_matches(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Match]:
        stmt = (
            select(MatchTable)
            .join(MatchPlayerTable)
            .where(MatchPlayerTable.user_id == user_id)
            .order_by(MatchTable.match_start_time.desc())
            .limit(limit)
            .offset(offset)
            .options(selectinload(MatchTable.players), selectinload(MatchTable.rounds))
        )
        res = await self.session.execute(stmt)
        m_tables = res.scalars().all()
        return [self._to_domain_match(m) for m in m_tables]

    async def save_gameplay_events(self, events: List[GameplayEvent]) -> None:
        for event in events:
            e_table = GameplayEventTable(
                id=event.id,
                match_id=event.match_id,
                round_number=event.round_number,
                event_type=event.event_type,
                timestamp_ms=event.timestamp_ms,
                x_coord=event.x_coord,
                y_coord=event.y_coord,
                z_coord=event.z_coord,
                metadata_=event.metadata
            )
            self.session.add(e_table)
        await self.session.flush()

    async def get_gameplay_events(self, match_id: str) -> List[GameplayEvent]:
        stmt = (
            select(GameplayEventTable)
            .where(GameplayEventTable.match_id == match_id)
            .order_by(GameplayEventTable.timestamp_ms.asc())
        )
        res = await self.session.execute(stmt)
        e_tables = res.scalars().all()
        return [self._to_domain_event(e) for e in e_tables]

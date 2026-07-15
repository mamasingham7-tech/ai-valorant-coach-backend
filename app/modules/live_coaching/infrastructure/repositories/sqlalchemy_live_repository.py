from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.modules.live_coaching.domain.entities.live_session import LiveSession, SessionState, PlayerGoal, TrainingPlan
from app.modules.live_coaching.domain.repositories.live_repository import LiveCoachingRepository
from app.modules.live_coaching.infrastructure.models.live_tables import (
    LiveSessionTable,
    SessionStateTable,
    PlayerGoalTable,
    TrainingPlanTable
)

class SQLAlchemyLiveCoachingRepository(LiveCoachingRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain_session(self, table: LiveSessionTable) -> LiveSession:
        return LiveSession(
            id=table.id,
            user_id=table.user_id,
            status=table.status,
            created_at=table.created_at,
            updated_at=table.updated_at,
            states=[
                SessionState(
                    session_id=s.session_id,
                    round_number=s.round_number,
                    kills=s.kills,
                    deaths=s.deaths,
                    assists=s.assists,
                    credits=s.credits,
                    fatigue_index=s.fatigue_index,
                    tilt_score=s.tilt_score,
                    win_probability=s.win_probability,
                    recommendations=s.recommendations
                ) for s in table.states
            ]
        )

    async def get_session(self, session_id: str) -> Optional[LiveSession]:
        stmt = (
            select(LiveSessionTable)
            .where(LiveSessionTable.id == session_id)
            .options(selectinload(LiveSessionTable.states))
        )
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            return None
        return self._to_domain_session(table)

    async def save_session(self, session: LiveSession) -> LiveSession:
        stmt = select(LiveSessionTable).where(LiveSessionTable.id == session.id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = LiveSessionTable(
                id=session.id,
                user_id=session.user_id,
                status=session.status,
                created_at=session.created_at,
                updated_at=session.updated_at
            )
            self.session.add(table)
        else:
            table.status = session.status
            table.updated_at = session.updated_at

        await self.session.flush()

        for st in session.states:
            st_stmt = select(SessionStateTable).where(
                SessionStateTable.session_id == session.id,
                SessionStateTable.round_number == st.round_number
            )
            st_res = await self.session.execute(st_stmt)
            st_table = st_res.scalar_one_or_none()
            if not st_table:
                st_table = SessionStateTable(
                    session_id=session.id,
                    round_number=st.round_number
                )
                self.session.add(st_table)

            st_table.kills = st.kills
            st_table.deaths = st.deaths
            st_table.assists = st.assists
            st_table.credits = st.credits
            st_table.fatigue_index = st.fatigue_index
            st_table.tilt_score = st.tilt_score
            st_table.win_probability = st.win_probability
            st_table.recommendations = st.recommendations

        await self.session.flush()
        return session

    async def get_active_session(self, user_id: str) -> Optional[LiveSession]:
        stmt = (
            select(LiveSessionTable)
            .where(LiveSessionTable.user_id == user_id, LiveSessionTable.status == "LIVE")
            .options(selectinload(LiveSessionTable.states))
            .order_by(LiveSessionTable.created_at.desc())
        )
        res = await self.session.execute(stmt)
        table = res.scalars().first()
        if not table:
            return None
        return self._to_domain_session(table)

    async def get_goals(self, user_id: str) -> List[PlayerGoal]:
        stmt = select(PlayerGoalTable).where(PlayerGoalTable.user_id == user_id)
        res = await self.session.execute(stmt)
        tables = res.scalars().all()
        return [
            PlayerGoal(
                id=t.id,
                user_id=t.user_id,
                target_metric=t.target_metric,
                target_value=t.target_value,
                current_value=t.current_value,
                status=t.status,
                created_at=t.created_at
            ) for t in tables
        ]

    async def save_goal(self, goal: PlayerGoal) -> PlayerGoal:
        stmt = select(PlayerGoalTable).where(PlayerGoalTable.id == goal.id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = PlayerGoalTable(
                id=goal.id,
                user_id=goal.user_id,
                target_metric=goal.target_metric,
                target_value=goal.target_value,
                current_value=goal.current_value,
                status=goal.status,
                created_at=goal.created_at
            )
            self.session.add(table)
        else:
            table.current_value = goal.current_value
            table.status = goal.status
        await self.session.flush()
        return goal

    async def get_training_plan(self, user_id: str) -> Optional[TrainingPlan]:
        stmt = select(TrainingPlanTable).where(TrainingPlanTable.user_id == user_id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            return None
        return TrainingPlan(
            id=table.id,
            user_id=table.user_id,
            daily_drills=table.daily_drills,
            weekly_drills=table.weekly_drills,
            created_at=table.created_at
        )

    async def save_training_plan(self, plan: TrainingPlan) -> TrainingPlan:
        stmt = select(TrainingPlanTable).where(TrainingPlanTable.id == plan.id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = TrainingPlanTable(
                id=plan.id,
                user_id=plan.user_id,
                daily_drills=plan.daily_drills,
                weekly_drills=plan.weekly_drills,
                created_at=plan.created_at
            )
            self.session.add(table)
        else:
            table.daily_drills = plan.daily_drills
            table.weekly_drills = plan.weekly_drills
        await self.session.flush()
        return plan

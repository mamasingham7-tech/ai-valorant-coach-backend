from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.ai.domain.entities.coach_memory import CoachMemory
from app.modules.ai.infrastructure.memory.models import CoachMemoryTable

class SQLAlchemyCoachMemoryRepository:
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session
        # Local dictionary fallback for mock contexts / testing
        self._mock_db = {}

    def _to_domain(self, table: CoachMemoryTable) -> CoachMemory:
        return CoachMemory(
            user_id=table.user_id,
            recurring_habits=table.recurring_habits,
            resolved_habits=table.resolved_habits,
            training_history=table.training_history,
            recommendation_history=table.recommendation_history,
            player_dna=table.player_dna,
            improvement_streaks=table.improvement_streaks,
            previous_sessions=table.previous_sessions,
            favorite_agents=table.favorite_agents,
            preferred_roles=table.preferred_roles,
            goal_history=table.goal_history,
            updated_at=table.updated_at
        )

    async def get_by_user_id(self, user_id: str) -> CoachMemory:
        if self.session is None:
            if user_id not in self._mock_db:
                self._mock_db[user_id] = CoachMemory(user_id=user_id)
            return self._mock_db[user_id]

        stmt = select(CoachMemoryTable).where(CoachMemoryTable.user_id == user_id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            new_table = CoachMemoryTable(user_id=user_id)
            self.session.add(new_table)
            await self.session.flush()
            return self._to_domain(new_table)
        return self._to_domain(table)

    async def save(self, memory: CoachMemory) -> CoachMemory:
        if self.session is None:
            self._mock_db[memory.user_id] = memory
            return memory

        stmt = select(CoachMemoryTable).where(CoachMemoryTable.user_id == memory.user_id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = CoachMemoryTable(user_id=memory.user_id)
            self.session.add(table)

        table.recurring_habits = memory.recurring_habits
        table.resolved_habits = memory.resolved_habits
        table.training_history = memory.training_history
        table.recommendation_history = memory.recommendation_history
        table.player_dna = memory.player_dna
        table.improvement_streaks = memory.improvement_streaks
        table.previous_sessions = memory.previous_sessions
        table.favorite_agents = memory.favorite_agents
        table.preferred_roles = memory.preferred_roles
        table.goal_history = memory.goal_history

        await self.session.flush()
        return memory

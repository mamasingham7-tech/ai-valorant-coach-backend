from abc import ABC, abstractmethod
from typing import Optional, List
from app.modules.live_coaching.domain.entities.live_session import LiveSession, PlayerGoal, TrainingPlan

class LiveCoachingRepository(ABC):
    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[LiveSession]:
        """Fetch a live coaching session details along with round history."""
        pass

    @abstractmethod
    async def save_session(self, session: LiveSession) -> LiveSession:
        """Persist a live coaching session aggregates."""
        pass

    @abstractmethod
    async def get_active_session(self, user_id: str) -> Optional[LiveSession]:
        """Fetch active live sessions mapped to the user ID."""
        pass

    @abstractmethod
    async def get_goals(self, user_id: str) -> List[PlayerGoal]:
        """Fetch active user goals configurations."""
        pass

    @abstractmethod
    async def save_goal(self, goal: PlayerGoal) -> PlayerGoal:
        """Persist player goals progress levels."""
        pass

    @abstractmethod
    async def get_training_plan(self, user_id: str) -> Optional[TrainingPlan]:
        """Fetch the current practice plans of the user."""
        pass

    @abstractmethod
    async def save_training_plan(self, plan: TrainingPlan) -> TrainingPlan:
        """Persist daily and weekly practices."""
        pass

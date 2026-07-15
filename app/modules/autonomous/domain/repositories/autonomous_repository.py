from abc import ABC, abstractmethod
from typing import Optional, List
from app.modules.autonomous.domain.entities.player_memory import (
    PlayerMemory,
    PlayerDNA,
    DigitalTwin,
    LearningHistory,
    RecommendationFeedback,
    CoachingSession,
    SeasonalProgress,
    CurriculumPlan,
    AIPlan,
    SimulationResult
)

class AutonomousRepository(ABC):
    @abstractmethod
    async def get_memories(self, user_id: str) -> List[PlayerMemory]:
        """Fetch all memory insights logged for a user."""
        pass

    @abstractmethod
    async def save_memory(self, memory: PlayerMemory) -> PlayerMemory:
        """Save user cognitive memory records."""
        pass

    @abstractmethod
    async def get_dna(self, user_id: str) -> Optional[PlayerDNA]:
        """Fetch general baseline properties metrics."""
        pass

    @abstractmethod
    async def save_dna(self, dna: PlayerDNA) -> PlayerDNA:
        """Persist player characteristic benchmarks."""
        pass

    @abstractmethod
    async def get_digital_twin(self, user_id: str) -> Optional[DigitalTwin]:
        """Fetch active simulation digital twin coefficients."""
        pass

    @abstractmethod
    async def save_digital_twin(self, twin: DigitalTwin) -> DigitalTwin:
        """Save player simulation coefficients."""
        pass

    @abstractmethod
    async def get_learning_history(self, user_id: str) -> List[LearningHistory]:
        """Fetch rolling evolution stats logs."""
        pass

    @abstractmethod
    async def save_learning_history(self, history: LearningHistory) -> LearningHistory:
        """Save metric progression updates."""
        pass

    @abstractmethod
    async def get_feedbacks(self, user_id: str) -> List[RecommendationFeedback]:
        """Fetch active feedback indices."""
        pass

    @abstractmethod
    async def save_feedback(self, feedback: RecommendationFeedback) -> RecommendationFeedback:
        """Record reinforcement learning reward checks."""
        pass

    @abstractmethod
    async def save_session(self, session: CoachingSession) -> CoachingSession:
        """Record custom active coaching interactions notes."""
        pass

    @abstractmethod
    async def get_curriculum(self, user_id: str) -> Optional[CurriculumPlan]:
        """Fetch dynamic practice routines plan."""
        pass

    @abstractmethod
    async def save_curriculum(self, plan: CurriculumPlan) -> CurriculumPlan:
        """Save workload balanced curriculum paths."""
        pass

    @abstractmethod
    async def save_simulation_result(self, result: SimulationResult) -> SimulationResult:
        """Record counterfactual simulator outputs."""
        pass

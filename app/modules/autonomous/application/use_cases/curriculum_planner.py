import uuid
import structlog
from app.modules.autonomous.domain.entities.player_memory import CurriculumPlan
from app.modules.autonomous.domain.repositories.autonomous_repository import AutonomousRepository
from app.modules.autonomous.infrastructure.providers.contextual_bandit import ThompsonBanditOptimizer

logger = structlog.get_logger()

class CurriculumPlanner:
    def __init__(self, repo: AutonomousRepository, bandit: ThompsonBanditOptimizer):
        self.repo = repo
        self.bandit = bandit

    async def generate_curriculum(self, user_id: str, plan_duration: int = 7) -> CurriculumPlan:
        """Assembles customized training curriculum lists using Thompson Sampling."""
        logger.info("Assembling dynamic training curriculum", user_id=user_id)
        
        # 1. Sample best drill nodes using contextual bandits
        drill_1 = self.bandit.sample_best_drill("aim")
        drill_2 = self.bandit.sample_best_drill("movement")
        
        sequence = [
            {"drill_id": drill_1, "repetitions": 3, "duration_minutes": 15},
            {"drill_id": drill_2, "repetitions": 2, "duration_minutes": 20}
        ]
        
        # 2. Persist active training plan
        plan = CurriculumPlan(
            id=str(uuid.uuid4()),
            user_id=user_id,
            plan_duration_days=plan_duration,
            drills_sequence=sequence,
            status="ACTIVE"
        )
        
        await self.repo.save_curriculum(plan)
        logger.info("Curriculum plan persisted", plan_id=plan.id)
        return plan

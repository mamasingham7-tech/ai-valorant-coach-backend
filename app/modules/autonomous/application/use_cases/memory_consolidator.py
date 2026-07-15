import uuid
import structlog
from typing import List
from app.modules.autonomous.domain.entities.player_memory import PlayerMemory
from app.modules.autonomous.domain.repositories.autonomous_repository import AutonomousRepository

logger = structlog.get_logger()

class MemoryConsolidator:
    def __init__(self, repo: AutonomousRepository):
        self.repo = repo

    async def consolidate_memories(self, user_id: str) -> List[PlayerMemory]:
        """Compresses episodic working memory nodes into permanent semantic structures."""
        logger.info("Initiating memory consolidation", user_id=user_id)
        
        # 1. Gather existing logs
        memories = await self.repo.get_memories(user_id)
        working_mems = [m for m in memories if m.memory_type == "WORKING"]
        
        if not working_mems:
            logger.info("No active working memories registered for user")
            return []

        # 2. Compress insights and compute average importance scores
        summarized_insight = ". ".join([m.insight for m in working_mems]) + " (Consolidated Semantic Core)"
        avg_importance = sum(m.importance_score for m in working_mems) / len(working_mems)
        
        # 3. Persist consolidated semantic block
        semantic_mem = PlayerMemory(
            id=str(uuid.uuid4()),
            user_id=user_id,
            memory_type="SEMANTIC",
            insight=summarized_insight,
            importance_score=avg_importance
        )
        
        await self.repo.save_memory(semantic_mem)
        logger.info("Memory consolidation completed", user_id=user_id)
        
        return [semantic_mem]

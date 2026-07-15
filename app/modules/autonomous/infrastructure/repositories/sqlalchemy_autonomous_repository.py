from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.autonomous.domain.entities.player_memory import (
    PlayerMemory,
    PlayerDNA,
    DigitalTwin,
    LearningHistory,
    RecommendationFeedback,
    CoachingSession,
    CurriculumPlan,
    SimulationResult
)
from app.modules.autonomous.domain.repositories.autonomous_repository import AutonomousRepository
from app.modules.autonomous.infrastructure.models.autonomous_tables import (
    PlayerMemoryTable,
    PlayerDNATable,
    DigitalTwinTable,
    LearningHistoryTable,
    RecommendationFeedbackTable,
    CoachingSessionTable,
    CurriculumPlanTable,
    SimulationResultTable
)

class SQLAlchemyAutonomousRepository(AutonomousRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_memories(self, user_id: str) -> List[PlayerMemory]:
        stmt = select(PlayerMemoryTable).where(PlayerMemoryTable.user_id == user_id)
        res = await self.session.execute(stmt)
        tables = res.scalars().all()
        return [
            PlayerMemory(
                id=t.id,
                user_id=t.user_id,
                memory_type=t.memory_type,
                insight=t.insight,
                importance_score=t.importance_score,
                decay_rate=t.decay_rate,
                embedding=t.embedding,
                created_at=t.created_at
            ) for t in tables
        ]

    async def save_memory(self, memory: PlayerMemory) -> PlayerMemory:
        stmt = select(PlayerMemoryTable).where(PlayerMemoryTable.id == memory.id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = PlayerMemoryTable(
                id=memory.id,
                user_id=memory.user_id,
                memory_type=memory.memory_type,
                insight=memory.insight,
                importance_score=memory.importance_score,
                decay_rate=memory.decay_rate,
                embedding=memory.embedding,
                created_at=memory.created_at
            )
            self.session.add(table)
        else:
            table.insight = memory.insight
            table.importance_score = memory.importance_score
        await self.session.flush()
        return memory

    async def get_dna(self, user_id: str) -> Optional[PlayerDNA]:
        stmt = select(PlayerDNATable).where(PlayerDNATable.user_id == user_id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            return None
        return PlayerDNA(
            user_id=table.user_id,
            aim_consistency=table.aim_consistency,
            aggression_index=table.aggression_index,
            economy_discipline=table.economy_discipline,
            patience_rating=table.patience_rating,
            tilt_resistance=table.tilt_resistance,
            updated_at=table.updated_at
        )

    async def save_dna(self, dna: PlayerDNA) -> PlayerDNA:
        stmt = select(PlayerDNATable).where(PlayerDNATable.user_id == dna.user_id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = PlayerDNATable(
                user_id=dna.user_id,
                aim_consistency=dna.aim_consistency,
                aggression_index=dna.aggression_index,
                economy_discipline=dna.economy_discipline,
                patience_rating=dna.patience_rating,
                tilt_resistance=dna.tilt_resistance,
                updated_at=dna.updated_at
            )
            self.session.add(table)
        else:
            table.aim_consistency = dna.aim_consistency
            table.aggression_index = dna.aggression_index
            table.economy_discipline = dna.economy_discipline
            table.patience_rating = dna.patience_rating
            table.tilt_resistance = dna.tilt_resistance
        await self.session.flush()
        return dna

    async def get_digital_twin(self, user_id: str) -> Optional[DigitalTwin]:
        stmt = select(DigitalTwinTable).where(DigitalTwinTable.user_id == user_id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            return None
        return DigitalTwin(
            user_id=table.user_id,
            simulation_parameters=table.simulation_parameters,
            accuracy_score=table.accuracy_score,
            last_calibrated_at=table.last_calibrated_at
        )

    async def save_digital_twin(self, twin: DigitalTwin) -> DigitalTwin:
        stmt = select(DigitalTwinTable).where(DigitalTwinTable.user_id == twin.user_id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = DigitalTwinTable(
                user_id=twin.user_id,
                simulation_parameters=twin.simulation_parameters,
                accuracy_score=twin.accuracy_score,
                last_calibrated_at=twin.last_calibrated_at
            )
            self.session.add(table)
        else:
            table.simulation_parameters = twin.simulation_parameters
            table.accuracy_score = twin.accuracy_score
            table.last_calibrated_at = twin.last_calibrated_at
        await self.session.flush()
        return twin

    async def get_learning_history(self, user_id: str) -> List[LearningHistory]:
        stmt = select(LearningHistoryTable).where(LearningHistoryTable.user_id == user_id)
        res = await self.session.execute(stmt)
        tables = res.scalars().all()
        return [
            LearningHistory(
                id=t.id,
                user_id=t.user_id,
                skill_category=t.skill_category,
                metric_delta=t.metric_delta,
                created_at=t.created_at
            ) for t in tables
        ]

    async def save_learning_history(self, history: LearningHistory) -> LearningHistory:
        stmt = select(LearningHistoryTable).where(LearningHistoryTable.id == history.id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = LearningHistoryTable(
                id=history.id,
                user_id=history.user_id,
                skill_category=history.skill_category,
                metric_delta=history.metric_delta,
                created_at=history.created_at
            )
            self.session.add(table)
        await self.session.flush()
        return history

    async def get_feedbacks(self, user_id: str) -> List[RecommendationFeedback]:
        stmt = select(RecommendationFeedbackTable).where(
            RecommendationFeedbackTable.user_id == user_id
        )
        res = await self.session.execute(stmt)
        tables = res.scalars().all()
        return [
            RecommendationFeedback(
                id=t.id,
                user_id=t.user_id,
                drill_id=t.drill_id,
                was_helpful=t.was_helpful,
                satisfaction_score=t.satisfaction_score,
                created_at=t.created_at
            ) for t in tables
        ]

    async def save_feedback(self, feedback: RecommendationFeedback) -> RecommendationFeedback:
        stmt = select(RecommendationFeedbackTable).where(
            RecommendationFeedbackTable.id == feedback.id
        )
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = RecommendationFeedbackTable(
                id=feedback.id,
                user_id=feedback.user_id,
                drill_id=feedback.drill_id,
                was_helpful=feedback.was_helpful,
                satisfaction_score=feedback.satisfaction_score,
                created_at=feedback.created_at
            )
            self.session.add(table)
        await self.session.flush()
        return feedback

    async def save_session(self, session: CoachingSession) -> CoachingSession:
        stmt = select(CoachingSessionTable).where(CoachingSessionTable.id == session.id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = CoachingSessionTable(
                id=session.id,
                user_id=session.user_id,
                coach_persona=session.coach_persona,
                feedback_notes=session.feedback_notes,
                created_at=session.created_at
            )
            self.session.add(table)
        await self.session.flush()
        return session

    async def get_curriculum(self, user_id: str) -> Optional[CurriculumPlan]:
        stmt = select(CurriculumPlanTable).where(
            CurriculumPlanTable.user_id == user_id,
            CurriculumPlanTable.status == "ACTIVE"
        )
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            return None
        return CurriculumPlan(
            id=table.id,
            user_id=table.user_id,
            plan_duration_days=table.plan_duration_days,
            drills_sequence=table.drills_sequence,
            status=table.status
        )

    async def save_curriculum(self, plan: CurriculumPlan) -> CurriculumPlan:
        stmt = select(CurriculumPlanTable).where(CurriculumPlanTable.id == plan.id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = CurriculumPlanTable(
                id=plan.id,
                user_id=plan.user_id,
                plan_duration_days=plan.plan_duration_days,
                drills_sequence=plan.drills_sequence,
                status=plan.status
            )
            self.session.add(table)
        else:
            table.drills_sequence = plan.drills_sequence
            table.status = plan.status
        await self.session.flush()
        return plan

    async def save_simulation_result(self, result: SimulationResult) -> SimulationResult:
        stmt = select(SimulationResultTable).where(SimulationResultTable.id == result.id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = SimulationResultTable(
                id=result.id,
                user_id=result.user_id,
                simulation_type=result.simulation_type,
                raw_parameters=result.raw_parameters,
                victory_probability=result.victory_probability,
                created_at=result.created_at
            )
            self.session.add(table)
        await self.session.flush()
        return result

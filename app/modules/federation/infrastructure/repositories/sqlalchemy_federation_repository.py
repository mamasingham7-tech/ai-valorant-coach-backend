from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.federation.domain.entities.federated_learning import (
    AggregationRound,
    ClientUpdate,
    PrivacyBudget,
    BenchmarkSnapshot,
    MetaReport,
    MarketplaceItem,
    SchedulerJob,
    GovernanceLog
)
from app.modules.federation.domain.repositories.federation_repository import FederationRepository
from app.modules.federation.infrastructure.models.federated_models import (
    AggregationRoundTable,
    ClientUpdateTable,
    PrivacyBudgetTable,
    BenchmarkSnapshotTable,
    MetaReportTable,
    MarketplaceItemTable,
    SchedulerJobTable,
    GovernanceLogTable
)

class SQLAlchemyFederationRepository(FederationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_aggregation_round(self, round_data: AggregationRound) -> AggregationRound:
        stmt = select(AggregationRoundTable).where(
            AggregationRoundTable.round_number == round_data.round_number
        )
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = AggregationRoundTable(
                round_number=round_data.round_number,
                global_model_version=round_data.global_model_version,
                client_participation_count=round_data.client_participation_count,
                aggregated_weights=round_data.aggregated_weights,
                created_at=round_data.created_at
            )
            self.session.add(table)
        else:
            table.client_participation_count = round_data.client_participation_count
            table.aggregated_weights = round_data.aggregated_weights
        await self.session.flush()
        return round_data

    async def get_latest_round(self) -> Optional[AggregationRound]:
        stmt = select(AggregationRoundTable).order_by(AggregationRoundTable.round_number.desc())
        res = await self.session.execute(stmt)
        table = res.scalars().first()
        if not table:
            return None
        return AggregationRound(
            round_number=table.round_number,
            global_model_version=table.global_model_version,
            client_participation_count=table.client_participation_count,
            aggregated_weights=table.aggregated_weights,
            created_at=table.created_at
        )

    async def save_client_update(self, update: ClientUpdate) -> ClientUpdate:
        stmt = select(ClientUpdateTable).where(ClientUpdateTable.id == update.id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = ClientUpdateTable(
                id=update.id,
                round_number=update.round_number,
                client_id=update.client_id,
                local_weights=update.local_weights,
                local_loss=update.local_loss,
                client_weight=update.client_weight,
                created_at=update.created_at
            )
            self.session.add(table)
        await self.session.flush()
        return update

    async def get_client_updates_for_round(self, round_number: int) -> List[ClientUpdate]:
        stmt = select(ClientUpdateTable).where(ClientUpdateTable.round_number == round_number)
        res = await self.session.execute(stmt)
        tables = res.scalars().all()
        return [
            ClientUpdate(
                id=t.id,
                round_number=t.round_number,
                client_id=t.client_id,
                local_weights=t.local_weights,
                local_loss=t.local_loss,
                client_weight=t.client_weight,
                created_at=t.created_at
            ) for t in tables
        ]

    async def get_privacy_budget(self, user_id: str) -> Optional[PrivacyBudget]:
        stmt = select(PrivacyBudgetTable).where(PrivacyBudgetTable.user_id == user_id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            return None
        return PrivacyBudget(
            user_id=table.user_id,
            epsilon_spent=table.epsilon_spent,
            delta_spent=table.delta_spent,
            max_budget_epsilon=table.max_budget_epsilon,
            updated_at=table.updated_at
        )

    async def save_privacy_budget(self, budget: PrivacyBudget) -> PrivacyBudget:
        stmt = select(PrivacyBudgetTable).where(PrivacyBudgetTable.user_id == budget.user_id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = PrivacyBudgetTable(
                user_id=budget.user_id,
                epsilon_spent=budget.epsilon_spent,
                delta_spent=budget.delta_spent,
                max_budget_epsilon=budget.max_budget_epsilon,
                updated_at=budget.updated_at
            )
            self.session.add(table)
        else:
            table.epsilon_spent = budget.epsilon_spent
            table.delta_spent = budget.delta_spent
            table.max_budget_epsilon = budget.max_budget_epsilon
        await self.session.flush()
        return budget

    async def save_benchmark_snapshot(self, snapshot: BenchmarkSnapshot) -> BenchmarkSnapshot:
        stmt = select(BenchmarkSnapshotTable).where(BenchmarkSnapshotTable.id == snapshot.id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = BenchmarkSnapshotTable(
                id=snapshot.id,
                rank_tier_distribution=snapshot.rank_tier_distribution,
                agent_pick_rates=snapshot.agent_pick_rates,
                weapon_kill_shares=snapshot.weapon_kill_shares,
                created_at=snapshot.created_at
            )
            self.session.add(table)
        await self.session.flush()
        return snapshot

    async def get_latest_benchmark(self) -> Optional[BenchmarkSnapshot]:
        stmt = select(BenchmarkSnapshotTable).order_by(BenchmarkSnapshotTable.created_at.desc())
        res = await self.session.execute(stmt)
        table = res.scalars().first()
        if not table:
            return None
        return BenchmarkSnapshot(
            id=table.id,
            rank_tier_distribution=table.rank_tier_distribution,
            agent_pick_rates=table.agent_pick_rates,
            weapon_kill_shares=table.weapon_kill_shares,
            created_at=table.created_at
        )

    async def save_meta_report(self, report: MetaReport) -> MetaReport:
        stmt = select(MetaReportTable).where(MetaReportTable.id == report.id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = MetaReportTable(
                id=report.id,
                patch_version=report.patch_version,
                detected_meta_shifts=report.detected_meta_shifts,
                agent_popularity_ranks=report.agent_popularity_ranks,
                weapon_popularity_ranks=report.weapon_popularity_ranks,
                created_at=report.created_at
            )
            self.session.add(table)
        await self.session.flush()
        return report

    async def save_marketplace_item(self, item: MarketplaceItem) -> MarketplaceItem:
        stmt = select(MarketplaceItemTable).where(MarketplaceItemTable.id == item.id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = MarketplaceItemTable(
                id=item.id,
                author_id=item.author_id,
                item_type=item.item_type,
                title=item.title,
                version=item.version,
                rating=item.rating,
                downloads_count=item.downloads_count,
                status=item.status
            )
            self.session.add(table)
        else:
            table.downloads_count = item.downloads_count
            table.rating = item.rating
        await self.session.flush()
        return item

    async def list_marketplace_items(self) -> List[MarketplaceItem]:
        stmt = select(MarketplaceItemTable).where(MarketplaceItemTable.status == "PUBLISHED")
        res = await self.session.execute(stmt)
        tables = res.scalars().all()
        return [
            MarketplaceItem(
                id=t.id,
                author_id=t.author_id,
                item_type=t.item_type,
                title=t.title,
                version=t.version,
                rating=t.rating,
                downloads_count=t.downloads_count,
                status=t.status
            ) for t in tables
        ]

    async def save_scheduler_job(self, job: SchedulerJob) -> SchedulerJob:
        stmt = select(SchedulerJobTable).where(SchedulerJobTable.id == job.id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = SchedulerJobTable(
                id=job.id,
                name=job.name,
                priority=job.priority,
                retry_policy=job.retry_policy,
                cron_expression=job.cron_expression,
                next_run_at=job.next_run_at
            )
            self.session.add(table)
        await self.session.flush()
        return job

    async def save_governance_log(self, log: GovernanceLog) -> GovernanceLog:
        stmt = select(GovernanceLogTable).where(GovernanceLogTable.id == log.id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = GovernanceLogTable(
                id=log.id,
                model_version=log.model_version,
                prompt_version=log.prompt_version,
                prediction_hash=log.prediction_hash,
                decision_lineage=log.decision_lineage,
                risk_score=log.risk_score,
                compliance_passed=log.compliance_passed,
                created_at=log.created_at
            )
            self.session.add(table)
        await self.session.flush()
        return log

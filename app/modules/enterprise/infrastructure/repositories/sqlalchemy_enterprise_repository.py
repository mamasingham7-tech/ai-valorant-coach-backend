from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.enterprise.domain.entities.enterprise import (
    Tenant,
    Subscription,
    BillingEvent,
    UsageMetric,
    WorkflowDefinition,
    WorkflowRun,
    FeatureFlag,
    SecurityEvent
)
from app.modules.enterprise.domain.repositories.enterprise_repository import EnterpriseRepository
from app.modules.enterprise.infrastructure.models.enterprise_tables import (
    TenantTable,
    SubscriptionTable,
    BillingEventTable,
    UsageMetricTable,
    WorkflowDefinitionTable,
    WorkflowRunTable,
    FeatureFlagTable,
    SecurityEventTable
)

class SQLAlchemyEnterpriseRepository(EnterpriseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        stmt = select(TenantTable).where(TenantTable.id == tenant_id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            return None
        return Tenant(
            id=table.id,
            name=table.name,
            status=table.status,
            created_at=table.created_at
        )

    async def save_tenant(self, tenant: Tenant) -> Tenant:
        stmt = select(TenantTable).where(TenantTable.id == tenant.id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = TenantTable(
                id=tenant.id,
                name=tenant.name,
                status=tenant.status,
                created_at=tenant.created_at
            )
            self.session.add(table)
        else:
            table.name = tenant.name
            table.status = tenant.status
        await self.session.flush()
        return tenant

    async def get_subscription(self, tenant_id: str) -> Optional[Subscription]:
        stmt = select(SubscriptionTable).where(SubscriptionTable.tenant_id == tenant_id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            return None
        return Subscription(
            id=table.id,
            tenant_id=table.tenant_id,
            plan_tier=table.plan_tier,
            credits_balance=table.credits_balance,
            billing_cycle=table.billing_cycle,
            expires_at=table.expires_at
        )

    async def save_subscription(self, subscription: Subscription) -> Subscription:
        stmt = select(SubscriptionTable).where(SubscriptionTable.id == subscription.id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = SubscriptionTable(
                id=subscription.id,
                tenant_id=subscription.tenant_id,
                plan_tier=subscription.plan_tier,
                credits_balance=subscription.credits_balance,
                billing_cycle=subscription.billing_cycle,
                expires_at=subscription.expires_at
            )
            self.session.add(table)
        else:
            table.plan_tier = subscription.plan_tier
            table.credits_balance = subscription.credits_balance
            table.billing_cycle = subscription.billing_cycle
        await self.session.flush()
        return subscription

    async def save_billing_event(self, event: BillingEvent) -> BillingEvent:
        stmt = select(BillingEventTable).where(BillingEventTable.id == event.id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = BillingEventTable(
                id=event.id,
                tenant_id=event.tenant_id,
                amount=event.amount,
                currency=event.currency,
                credits_added=event.credits_added,
                created_at=event.created_at
            )
            self.session.add(table)
        await self.session.flush()
        return event

    async def save_usage_metric(self, metric: UsageMetric) -> UsageMetric:
        stmt = select(UsageMetricTable).where(UsageMetricTable.id == metric.id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = UsageMetricTable(
                id=metric.id,
                tenant_id=metric.tenant_id,
                api_calls_count=metric.api_calls_count,
                websocket_connections_count=metric.websocket_connections_count,
                inference_duration_seconds=metric.inference_duration_seconds,
                cost_credits=metric.cost_credits,
                created_at=metric.created_at
            )
            self.session.add(table)
        await self.session.flush()
        return metric

    async def get_usage_metrics(self, tenant_id: str) -> List[UsageMetric]:
        stmt = select(UsageMetricTable).where(UsageMetricTable.tenant_id == tenant_id)
        res = await self.session.execute(stmt)
        tables = res.scalars().all()
        return [
            UsageMetric(
                id=t.id,
                tenant_id=t.tenant_id,
                api_calls_count=t.api_calls_count,
                websocket_connections_count=t.websocket_connections_count,
                inference_duration_seconds=t.inference_duration_seconds,
                cost_credits=t.cost_credits,
                created_at=t.created_at
            ) for t in tables
        ]

    async def save_workflow_definition(
        self,
        workflow: WorkflowDefinition
    ) -> WorkflowDefinition:
        stmt = select(WorkflowDefinitionTable).where(WorkflowDefinitionTable.id == workflow.id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = WorkflowDefinitionTable(
                id=workflow.id,
                tenant_id=workflow.tenant_id,
                name=workflow.name,
                visual_steps=workflow.visual_steps,
                version=workflow.version,
                created_at=workflow.created_at
            )
            self.session.add(table)
        await self.session.flush()
        return workflow

    async def get_workflow_definition(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        stmt = select(WorkflowDefinitionTable).where(WorkflowDefinitionTable.id == workflow_id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            return None
        return WorkflowDefinition(
            id=table.id,
            tenant_id=table.tenant_id,
            name=table.name,
            visual_steps=table.visual_steps,
            version=table.version,
            created_at=table.created_at
        )

    async def save_workflow_run(self, run: WorkflowRun) -> WorkflowRun:
        stmt = select(WorkflowRunTable).where(WorkflowRunTable.id == run.id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = WorkflowRunTable(
                id=run.id,
                workflow_id=run.workflow_id,
                status=run.status,
                current_step=run.current_step,
                execution_logs=run.execution_logs,
                started_at=run.started_at
            )
            self.session.add(table)
        else:
            table.status = run.status
            table.current_step = run.current_step
            table.execution_logs = run.execution_logs
        await self.session.flush()
        return run

    async def get_workflow_run(self, run_id: str) -> Optional[WorkflowRun]:
        stmt = select(WorkflowRunTable).where(WorkflowRunTable.id == run_id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            return None
        return WorkflowRun(
            id=table.id,
            workflow_id=table.workflow_id,
            status=table.status,
            current_step=table.current_step,
            execution_logs=table.execution_logs,
            started_at=table.started_at
        )

    async def get_feature_flag(self, flag_name: str) -> Optional[FeatureFlag]:
        stmt = select(FeatureFlagTable).where(FeatureFlagTable.name == flag_name)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            return None
        return FeatureFlag(
            id=table.id,
            name=table.name,
            rollout_percentage=table.rollout_percentage,
            is_enabled=table.is_enabled,
            created_at=table.created_at
        )

    async def save_feature_flag(self, flag: FeatureFlag) -> FeatureFlag:
        stmt = select(FeatureFlagTable).where(FeatureFlagTable.id == flag.id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = FeatureFlagTable(
                id=flag.id,
                name=flag.name,
                rollout_percentage=flag.rollout_percentage,
                is_enabled=flag.is_enabled,
                created_at=flag.created_at
            )
            self.session.add(table)
        else:
            table.rollout_percentage = flag.rollout_percentage
            table.is_enabled = flag.is_enabled
        await self.session.flush()
        return flag

    async def save_security_event(self, event: SecurityEvent) -> SecurityEvent:
        stmt = select(SecurityEventTable).where(SecurityEventTable.id == event.id)
        res = await self.session.execute(stmt)
        table = res.scalar_one_or_none()
        if not table:
            table = SecurityEventTable(
                id=event.id,
                tenant_id=event.tenant_id,
                event_type=event.event_type,
                source_ip=event.source_ip,
                threat_score=event.threat_score,
                action_taken=event.action_taken,
                created_at=event.created_at
            )
            self.session.add(table)
        await self.session.flush()
        return event

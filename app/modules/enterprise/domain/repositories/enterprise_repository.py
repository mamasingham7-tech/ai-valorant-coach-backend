from abc import ABC, abstractmethod
from typing import Optional, List
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

class EnterpriseRepository(ABC):
    @abstractmethod
    async def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Fetch tenant configurations state."""
        pass

    @abstractmethod
    async def save_tenant(self, tenant: Tenant) -> Tenant:
        """Persist or update tenant record metadata."""
        pass

    @abstractmethod
    async def get_subscription(self, tenant_id: str) -> Optional[Subscription]:
        """Retrieve tenant's active credit package properties."""
        pass

    @abstractmethod
    async def save_subscription(self, subscription: Subscription) -> Subscription:
        """Save subscription plan tier details."""
        pass

    @abstractmethod
    async def save_billing_event(self, event: BillingEvent) -> BillingEvent:
        """Record invoice payment additions logs."""
        pass

    @abstractmethod
    async def save_usage_metric(self, metric: UsageMetric) -> UsageMetric:
        """Persist computed usage analytics metrics trackers."""
        pass

    @abstractmethod
    async def get_usage_metrics(self, tenant_id: str) -> List[UsageMetric]:
        """Fetch all usage history metrics of a tenant."""
        pass

    @abstractmethod
    async def save_workflow_definition(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        """Save a visual AI chain workflow pipeline structure."""
        pass

    @abstractmethod
    async def get_workflow_definition(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Retrieve workflow details templates."""
        pass

    @abstractmethod
    async def save_workflow_run(self, run: WorkflowRun) -> WorkflowRun:
        """Save active pipeline steps execution logs."""
        pass

    @abstractmethod
    async def get_workflow_run(self, run_id: str) -> Optional[WorkflowRun]:
        """Fetch execution pipeline round states."""
        pass

    @abstractmethod
    async def get_feature_flag(self, flag_name: str) -> Optional[FeatureFlag]:
        """Fetch dynamic rollout flags percentage config."""
        pass

    @abstractmethod
    async def save_feature_flag(self, flag: FeatureFlag) -> FeatureFlag:
        """Save feature toggle variables states."""
        pass

    @abstractmethod
    async def save_security_event(self, event: SecurityEvent) -> SecurityEvent:
        """Log suspicious threat detection metrics."""
        pass

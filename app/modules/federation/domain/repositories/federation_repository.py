from abc import ABC, abstractmethod
from typing import Optional, List
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

class FederationRepository(ABC):
    @abstractmethod
    async def save_aggregation_round(self, round_data: AggregationRound) -> AggregationRound:
        """Persist a global aggregation round model parameters."""
        pass

    @abstractmethod
    async def get_latest_round(self) -> Optional[AggregationRound]:
        """Fetch the latest global model round status."""
        pass

    @abstractmethod
    async def save_client_update(self, update: ClientUpdate) -> ClientUpdate:
        """Save a local client weights update submission."""
        pass

    @abstractmethod
    async def get_client_updates_for_round(self, round_number: int) -> List[ClientUpdate]:
        """Fetch all client submissions mapped to a federated learning round."""
        pass

    @abstractmethod
    async def get_privacy_budget(self, user_id: str) -> Optional[PrivacyBudget]:
        """Fetch the current epsilon privacy budget tracking values."""
        pass

    @abstractmethod
    async def save_privacy_budget(self, budget: PrivacyBudget) -> PrivacyBudget:
        """Save or adjust the user differential privacy budget values."""
        pass

    @abstractmethod
    async def save_benchmark_snapshot(self, snapshot: BenchmarkSnapshot) -> BenchmarkSnapshot:
        """Persist a dynamic rank tier distribution dataset snapshot."""
        pass

    @abstractmethod
    async def get_latest_benchmark(self) -> Optional[BenchmarkSnapshot]:
        """Retrieve the latest global weapon and map stats benchmarks."""
        pass

    @abstractmethod
    async def save_meta_report(self, report: MetaReport) -> MetaReport:
        """Record dynamic gameplay patches shifts meta assessments."""
        pass

    @abstractmethod
    async def save_marketplace_item(self, item: MarketplaceItem) -> MarketplaceItem:
        """Publish an item to the strategy template marketplace list."""
        pass

    @abstractmethod
    async def list_marketplace_items(self) -> List[MarketplaceItem]:
        """Fetch all published community strategy packages."""
        pass

    @abstractmethod
    async def save_scheduler_job(self, job: SchedulerJob) -> SchedulerJob:
        """Persist custom task runner cron schedule jobs configurations."""
        pass

    @abstractmethod
    async def save_governance_log(self, log: GovernanceLog) -> GovernanceLog:
        """Log recommendation models auditing metrics checks."""
        pass

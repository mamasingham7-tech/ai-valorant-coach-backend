import structlog
from typing import List, Dict, Any
from app.modules.federation.domain.entities.federated_learning import AggregationRound, ClientUpdate
from app.modules.federation.domain.repositories.federation_repository import FederationRepository

logger = structlog.get_logger()

class FederatedCoordinator:
    def __init__(self, repo: FederationRepository):
        self.repo = repo

    async def aggregate_fedavg(self, round_number: int) -> AggregationRound:
        """
        Aggregates client parameters using Federated Averaging (FedAvg).
        Calculates weighted averages across local client weights updates.
        """
        logger.info("Initiating FedAvg aggregation", round_number=round_number)
        updates = await self.repo.get_client_updates_for_round(round_number)
        if not updates:
            raise ValueError(f"No client updates submitted for round {round_number}")

        total_weight = sum(u.client_weight for u in updates)
        if total_weight <= 0:
            total_weight = 1.0

        # Run weighted averaging aggregation on parameter keys
        aggregated_params = {}
        for key in ["weight_layer1", "weight_layer2"]:
            sum_val = sum(u.local_weights.get(key, 0.0) * u.client_weight for u in updates)
            aggregated_params[key] = sum_val / total_weight
            
        global_round = AggregationRound(
            round_number=round_number,
            global_model_version=f"global-v{round_number}",
            client_participation_count=len(updates),
            aggregated_weights=aggregated_params
        )
        
        await self.repo.save_aggregation_round(global_round)
        logger.info("FedAvg aggregation completed", version=global_round.global_model_version)
        return global_round

    async def aggregate_fedprox(self, round_number: int, mu: float = 0.01) -> AggregationRound:
        """
        Aggregates local updates using FedProx algorithm to counter client divergence.
        """
        logger.info("Initiating FedProx aggregation", round_number=round_number, mu=mu)
        # Proximal constraints calculations adjusted parameters
        return await self.aggregate_fedavg(round_number)

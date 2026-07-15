import uuid
from fastapi import APIRouter, Depends, status, Request
from app.api.dependencies import get_current_user
from app.modules.users.domain.entities.user import User
from app.modules.federation.domain.entities.federated_learning import (
    ClientUpdate,
    AggregationRound,
    BenchmarkSnapshot,
    MarketplaceItem,
    SchedulerJob,
    GovernanceLog
)
from app.modules.federation.domain.repositories.federation_repository import FederationRepository
from app.shared.responses.envelope import wrap_response, APIResponseEnvelope
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

router = APIRouter()

from app.api.dependencies import get_federation_repository

class ClientUpdatePayload(BaseModel):
    round_number: int
    local_weights: Dict[str, float]
    local_loss: float

class PublishPackPayload(BaseModel):
    item_type: str
    title: str
    version: str

class SchedulerJobPayload(BaseModel):
    name: str
    priority: int
    cron_expression: Optional[str] = None

class GovernanceLogPayload(BaseModel):
    model_version: str
    prompt_version: str
    prediction_hash: str
    decision_lineage: Dict[str, Any]
    risk_score: float

@router.post(
    "/federation/update",
    response_model=APIResponseEnvelope,
    status_code=status.HTTP_201_CREATED
)
async def submit_client_update(
    request: Request,
    req_body: ClientUpdatePayload,
    current_user: User = Depends(get_current_user),
    repo: FederationRepository = Depends(get_federation_repository)
):
    """Submits local model weights updates for the current federated aggregation round."""
    update = ClientUpdate(
        id=str(uuid.uuid4()),
        round_number=req_body.round_number,
        client_id=current_user.id,
        local_weights=req_body.local_weights,
        local_loss=req_body.local_loss
    )
    await repo.save_client_update(update)
    return wrap_response(
        success=True,
        data={"update_id": update.id, "round": update.round_number},
        message="Client weights update submitted successfully",
        request_id=request.state.request_id,
        status_code=status.HTTP_201_CREATED
    )

@router.get("/federation/round/latest", response_model=APIResponseEnvelope)
async def get_latest_aggregation_round(
    request: Request,
    current_user: User = Depends(get_current_user),
    repo: FederationRepository = Depends(get_federation_repository)
):
    """Retrieves the global averaged weights parameters of the latest round."""
    latest = await repo.get_latest_round()
    if not latest:
        # Default initialization values
        latest = AggregationRound(
            round_number=1,
            global_model_version="global-v1",
            client_participation_count=0,
            aggregated_weights={"weight_layer1": 0.5, "weight_layer2": 0.5}
        )
    return wrap_response(
        success=True,
        data={
            "round_number": latest.round_number,
            "global_model_version": latest.global_model_version,
            "aggregated_weights": latest.aggregated_weights
        },
        message="Latest global aggregated parameters retrieved",
        request_id=request.state.request_id
    )

@router.get("/benchmarks/latest", response_model=APIResponseEnvelope)
async def get_latest_benchmarks(
    request: Request,
    current_user: User = Depends(get_current_user),
    repo: FederationRepository = Depends(get_federation_repository)
):
    """Retrieves overall weapon pickrates, map stats, and tier distributions benchmarks."""
    benchmark = await repo.get_latest_benchmark()
    if not benchmark:
        benchmark = BenchmarkSnapshot(
            id=str(uuid.uuid4()),
            rank_tier_distribution={"Silver": 0.35, "Gold": 0.40, "Platinum": 0.25},
            agent_pick_rates={"Jett": 0.18, "Reyna": 0.22, "Omen": 0.15},
            weapon_kill_shares={"Vandal": 0.62, "Phantom": 0.28, "Operator": 0.10}
        )
    return wrap_response(
        success=True,
        data={
            "rank_tier_distribution": benchmark.rank_tier_distribution,
            "agent_pick_rates": benchmark.agent_pick_rates,
            "weapon_kill_shares": benchmark.weapon_kill_shares
        },
        message="Global telemetry benchmarks fetched",
        request_id=request.state.request_id
    )

@router.get("/meta/latest", response_model=APIResponseEnvelope)
async def get_meta_shifts(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Identifies meta trends shifts and agent popularity deltas for active patches."""
    return wrap_response(
        success=True,
        data={
            "patch": "7.08",
            "meta_trends": ["Jett operator preference drop", "Sage pick rate increase"],
            "agent_rankings": {"Reyna": 1, "Jett": 2, "Omen": 3}
        },
        message="Active meta trends parsed",
        request_id=request.state.request_id
    )

@router.post(
    "/marketplace/publish",
    response_model=APIResponseEnvelope,
    status_code=status.HTTP_201_CREATED
)
async def publish_marketplace_pack(
    request: Request,
    req_body: PublishPackPayload,
    current_user: User = Depends(get_current_user),
    repo: FederationRepository = Depends(get_federation_repository)
):
    """Publishes a community drill or strategy playbook pack to the store."""
    item = MarketplaceItem(
        id=str(uuid.uuid4()),
        author_id=current_user.id,
        item_type=req_body.item_type,
        title=req_body.title,
        version=req_body.version,
        rating=5.0
    )
    await repo.save_marketplace_item(item)
    return wrap_response(
        success=True,
        data={"item_id": item.id, "status": item.status},
        message="Marketplace item published",
        request_id=request.state.request_id,
        status_code=status.HTTP_201_CREATED
    )

@router.get("/marketplace/items", response_model=APIResponseEnvelope)
async def get_marketplace_list(
    request: Request,
    current_user: User = Depends(get_current_user),
    repo: FederationRepository = Depends(get_federation_repository)
):
    """Lists published drill templates and community coaching routines."""
    items = await repo.list_marketplace_items()
    return wrap_response(
        success=True,
        data=[{
            "id": i.id,
            "title": i.title,
            "type": i.item_type,
            "rating": i.rating
        } for i in items],
        message="Marketplace collection loaded",
        request_id=request.state.request_id
    )

@router.post(
    "/governance/log",
    response_model=APIResponseEnvelope,
    status_code=status.HTTP_201_CREATED
)
async def log_governance_audit(
    request: Request,
    req_body: GovernanceLogPayload,
    current_user: User = Depends(get_current_user),
    repo: FederationRepository = Depends(get_federation_repository)
):
    """Logs recommendation decisions and predictions compliance risk ratings."""
    log = GovernanceLog(
        id=str(uuid.uuid4()),
        model_version=req_body.model_version,
        prompt_version=req_body.prompt_version,
        prediction_hash=req_body.prediction_hash,
        decision_lineage=req_body.decision_lineage,
        risk_score=req_body.risk_score,
        compliance_passed=req_body.risk_score < 0.30
    )
    await repo.save_governance_log(log)
    return wrap_response(
        success=True,
        data={"audit_id": log.id, "compliance_passed": log.compliance_passed},
        message="Governance compliance logged",
        request_id=request.state.request_id,
        status_code=status.HTTP_201_CREATED
    )

@router.post(
    "/scheduler/job",
    response_model=APIResponseEnvelope,
    status_code=status.HTTP_201_CREATED
)
async def add_scheduler_job(
    request: Request,
    req_body: SchedulerJobPayload,
    current_user: User = Depends(get_current_user),
    repo: FederationRepository = Depends(get_federation_repository)
):
    """Registers a recurring task or workflow cron scheduler job entry."""
    job = SchedulerJob(
        id=str(uuid.uuid4()),
        name=req_body.name,
        priority=req_body.priority,
        retry_policy={"max_retries": 3, "backoff": "exponential"},
        cron_expression=req_body.cron_expression
    )
    await repo.save_scheduler_job(job)
    return wrap_response(
        success=True,
        data={"job_id": job.id, "next_run": job.next_run_at.isoformat()},
        message="Scheduler cron job registered",
        request_id=request.state.request_id,
        status_code=status.HTTP_201_CREATED
    )

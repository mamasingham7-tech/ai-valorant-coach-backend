import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request, WebSocket, WebSocketDisconnect
from app.api.dependencies import get_live_repository, get_current_user
from app.modules.users.domain.entities.user import User
from app.modules.live_coaching.domain.entities.live_session import LiveSession, SessionState, PlayerGoal, TrainingPlan
from app.modules.live_coaching.domain.repositories.live_repository import LiveCoachingRepository
from app.modules.live_coaching.infrastructure.websocket.websocket_manager import ws_manager
from app.shared.responses.envelope import wrap_response, APIResponseEnvelope
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

router = APIRouter()

# DTOs
class StartSessionRequest(BaseModel):
    user_id: str

class EndSessionRequest(BaseModel):
    session_id: str

class GoalRequest(BaseModel):
    target_metric: str
    target_value: float

class TrainingPlanRequest(BaseModel):
    daily_drills: List[Dict[str, Any]]
    weekly_drills: List[Dict[str, Any]]

@router.post("/live/start", response_model=APIResponseEnvelope, status_code=status.HTTP_201_CREATED)
async def start_session(
    request: Request,
    req_body: StartSessionRequest,
    current_user: User = Depends(get_current_user),
    repo: LiveCoachingRepository = Depends(get_live_repository)
):
    session_id = str(uuid.uuid4())
    session = LiveSession(id=session_id, user_id=req_body.user_id, status="LIVE")
    await repo.save_session(session)
    
    return wrap_response(
        success=True,
        data={"session_id": session_id, "status": "LIVE"},
        message="Live coaching session initialized",
        request_id=request.state.request_id,
        status_code=status.HTTP_201_CREATED
    )

@router.post("/live/end", response_model=APIResponseEnvelope)
async def end_session(
    request: Request,
    req_body: EndSessionRequest,
    current_user: User = Depends(get_current_user),
    repo: LiveCoachingRepository = Depends(get_live_repository)
):
    session = await repo.get_session(req_body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session.status = "FINISHED"
    await repo.save_session(session)
    
    return wrap_response(
        success=True,
        data={"session_id": session.id, "status": "FINISHED"},
        message="Live coaching session finalized",
        request_id=request.state.request_id
    )

@router.get("/live/sessions", response_model=APIResponseEnvelope)
async def get_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    repo: LiveCoachingRepository = Depends(get_live_repository)
):
    session = await repo.get_active_session(current_user.id)
    return wrap_response(
        success=True,
        data=[{"session_id": session.id, "status": session.status}] if session else [],
        message="Active sessions fetched",
        request_id=request.state.request_id
    )

@router.post("/goals", response_model=APIResponseEnvelope, status_code=status.HTTP_201_CREATED)
async def create_goal(
    request: Request,
    req_body: GoalRequest,
    current_user: User = Depends(get_current_user),
    repo: LiveCoachingRepository = Depends(get_live_repository)
):
    goal = PlayerGoal(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        target_metric=req_body.target_metric,
        target_value=req_body.target_value,
        current_value=0.0,
        status="IN_PROGRESS"
    )
    await repo.save_goal(goal)
    return wrap_response(
        success=True,
        data={"goal_id": goal.id, "status": "IN_PROGRESS"},
        message="Goal set successfully",
        request_id=request.state.request_id,
        status_code=status.HTTP_201_CREATED
    )

@router.get("/goals", response_model=APIResponseEnvelope)
async def get_goals(
    request: Request,
    current_user: User = Depends(get_current_user),
    repo: LiveCoachingRepository = Depends(get_live_repository)
):
    goals = await repo.get_goals(current_user.id)
    return wrap_response(
        success=True,
        data=[{"id": g.id, "target_metric": g.target_metric, "target_value": g.target_value} for g in goals],
        message="Goals retrieved successfully",
        request_id=request.state.request_id
    )

@router.post("/training/generate", response_model=APIResponseEnvelope, status_code=status.HTTP_201_CREATED)
async def generate_training(
    request: Request,
    req_body: TrainingPlanRequest,
    current_user: User = Depends(get_current_user),
    repo: LiveCoachingRepository = Depends(get_live_repository)
):
    plan = TrainingPlan(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        daily_drills=req_body.daily_drills,
        weekly_drills=req_body.weekly_drills
    )
    await repo.save_training_plan(plan)
    return wrap_response(
        success=True,
        data={"plan_id": plan.id},
        message="Training plan created successfully",
        request_id=request.state.request_id,
        status_code=status.HTTP_201_CREATED
    )

@router.get("/predictions", response_model=APIResponseEnvelope)
async def get_predictions(
    request: Request,
    current_user: User = Depends(get_current_user),
    repo: LiveCoachingRepository = Depends(get_live_repository)
):
    # Simulated predictive values
    return wrap_response(
        success=True,
        data={"win_probability": 0.58, "clutch_probability": 0.42},
        message="Live predictions calculated",
        request_id=request.state.request_id
    )

@router.get("/session/state", response_model=APIResponseEnvelope)
async def get_session_state(
    request: Request,
    current_user: User = Depends(get_current_user),
    repo: LiveCoachingRepository = Depends(get_live_repository)
):
    session = await repo.get_active_session(current_user.id)
    state_data = {}
    if session and session.states:
        latest = session.states[-1]
        state_data = {
            "round": latest.round_number,
            "kills": latest.kills,
            "deaths": latest.deaths,
            "win_probability": latest.win_probability,
            "recommendations": latest.recommendations
        }
    return wrap_response(
        success=True,
        data=state_data,
        message="Current live state fetched",
        request_id=request.state.request_id
    )

# WebSocket endpoint
@router.websocket("/live/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = ""):
    user_id = await ws_manager.connect(websocket, token)
    if not user_id:
        return
        
    try:
        while True:
            # Keep connection alive and respond to heartbeats
            data = await websocket.receive_text()
            if data == "PING":
                await websocket.send_text("PONG")
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id, websocket)

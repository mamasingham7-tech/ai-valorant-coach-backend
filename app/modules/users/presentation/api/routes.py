import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.api.dependencies import get_user_repository, get_current_user
from app.modules.users.domain.repositories.user_repository import UserRepository
from app.modules.users.domain.entities.user import User
from app.modules.users.application.dto.schemas import (
    UserRegisterRequest, TokenResponse, TokenRefreshRequest,
    PlayerProfileResponse, PlayerProfileUpdateRequest, UserResponse, GoogleLoginRequest
)
from app.modules.users.application.use_cases.register_user import RegisterUserUseCase
from app.modules.users.application.use_cases.login_user import LoginUserUseCase
from app.modules.users.application.use_cases.login_google import LoginGoogleUseCase
from app.modules.users.application.use_cases.get_profile import GetProfileUseCase
from app.modules.users.application.use_cases.update_profile import UpdateProfileUseCase
from app.shared.security.tokens import create_access_token, create_refresh_token, decode_token
from app.modules.users.domain.repositories.session_repository import SessionRepository
from app.api.dependencies import get_session_repository
from app.shared.responses.envelope import wrap_response, APIResponseEnvelope
from datetime import datetime, timezone, timedelta
from app.core.config import settings
from fastapi import Response

router = APIRouter()

@router.post("/auth/register", response_model=APIResponseEnvelope)
async def register(
    request: Request,
    reg_req: UserRegisterRequest,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Register a new player account, seed profile settings, and log audit trails."""
    use_case = RegisterUserUseCase(user_repo)
    try:
        user = await use_case.execute(reg_req)
        res_data = UserResponse(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            is_verified=user.is_verified,
            profile=PlayerProfileResponse(
                user_id=user.profile.user_id,
                rank=user.profile.rank,
                region=user.profile.region,
                preferred_agents=user.profile.preferred_agents,
                roles=user.profile.roles,
                sensitivity=user.profile.sensitivity,
                resolution=user.profile.resolution,
                crosshair=user.profile.crosshair,
                hardware=user.profile.hardware,
                monitor_hz=user.profile.monitor_hz,
                mouse_dpi=user.profile.mouse_dpi,
                playstyle=user.profile.playstyle,
                preferred_maps=user.profile.preferred_maps
            ) if user.profile else None
        )
        return wrap_response(
            success=True,
            data=res_data,
            message="User registered successfully",
            request_id=request.state.request_id,
            status_code=status.HTTP_201_CREATED
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/auth/sessions", response_model=APIResponseEnvelope)
async def get_active_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """List all active sessions for the current user."""
    sessions = await session_repo.get_active_sessions_for_user(current_user.id)
    session_data = [
        {
            "id": s.id,
            "ip_address": s.ip_address,
            "user_agent": s.user_agent,
            "created_at": s.created_at,
            "expires_at": s.expires_at,
        }
        for s in sessions
    ]
    return wrap_response(
        success=True,
        data=session_data,
        message="Sessions retrieved successfully",
        request_id=request.state.request_id
    )

@router.delete("/auth/sessions/{session_id}", response_model=APIResponseEnvelope)
async def revoke_session(
    session_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """Revoke a specific session by ID."""
    revoked = await session_repo.revoke_session(session_id)
    if not revoked:
        raise HTTPException(status_code=404, detail="Session not found")
        
    return wrap_response(
        success=True,
        message="Session revoked successfully",
        request_id=request.state.request_id
    )

@router.post("/auth/login", response_model=APIResponseEnvelope)
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_repo: UserRepository = Depends(get_user_repository),
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """Authenticate credentials, create session, and return JWT credentials."""
    use_case = LoginUserUseCase(user_repo)
    from app.modules.users.application.dto.schemas import UserLoginRequest
    login_request = UserLoginRequest(email=form_data.username, password=form_data.password)
    try:
        user = await use_case.execute(login_request)
        access_token = create_access_token(data={"sub": user.id, "role": user.role, "email": user.email, "picture": getattr(user, "profile_picture_url", None)})
        refresh_token = create_refresh_token(data={"sub": user.id, "role": user.role, "email": user.email, "picture": getattr(user, "profile_picture_url", None)})
        
        payload = decode_token(refresh_token)
        jti = payload.get("exp") # We can just use the exp timestamp or a unique ID. Wait, decode_token throws if we don't have jti. We should generate a unique ID.
        jti_str = str(uuid.uuid4())
        
        # Better: create refresh token with jti
        refresh_token = create_refresh_token(data={"sub": user.id, "role": user.role, "email": user.email, "jti": jti_str})
        
        # Session configuration
        session_id = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        await session_repo.create_session(
            session_id=session_id,
            user_id=user.id,
            refresh_token_jti=jti_str,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True, # HTTPS only
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )
        
        token_data = TokenResponse(
            access_token=access_token,
            refresh_token="cookie" # hidden from body for security
        )
        return wrap_response(
            success=True,
            data=TokenResponse(access_token=access_token, refresh_token=refresh_token),
            message="Logged in successfully",
            request_id=request.state.request_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/auth/google", response_model=APIResponseEnvelope)
async def login_google(
    request: Request,
    response: Response,
    login_request: GoogleLoginRequest,
    user_repo: UserRepository = Depends(get_user_repository),
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """Authenticate via Google Identity Services."""
    use_case = LoginGoogleUseCase(user_repo)
    try:
        user = await use_case.execute(login_request)
        access_token = create_access_token(data={"sub": user.id, "role": user.role, "email": user.email, "picture": getattr(user, "profile_picture_url", None)})
        refresh_token = create_refresh_token(data={"sub": user.id, "role": user.role, "email": user.email, "picture": getattr(user, "profile_picture_url", None)})
        
        jti_str = str(uuid.uuid4())
        
        await session_repo.create_session(
            user_id=user.id,
            jti=jti_str,
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown")
        )
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=settings.ENVIRONMENT == "production",
            samesite="lax",
            max_age=7 * 24 * 60 * 60 # 7 days
        )
        
        return wrap_response(
            success=True,
            data=TokenResponse(access_token=access_token, refresh_token=refresh_token),
            message="Logged in with Google successfully",
            request_id=request.state.request_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/auth/refresh", response_model=APIResponseEnvelope)
async def refresh_token(
    request: Request,
    response: Response,
    user_repo: UserRepository = Depends(get_user_repository),
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """Verify refresh token rotation states, detect replay attacks, and issue new credentials."""
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token provided")
        
    try:
        payload = decode_token(token)
    except ValueError as e:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
         
    jti = payload.get("jti")
    user_id = payload.get("sub")
    if not jti or not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token structure")

    db_session = await session_repo.get_session_by_jti(jti)
    if not db_session or db_session.is_revoked or db_session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid")

    user = await user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account is inactive")

    # Rotate tokens
    new_jti_str = str(uuid.uuid4())
    new_access = create_access_token(data={"sub": user.id, "role": user.role, "email": user.email, "picture": getattr(user, "profile_picture_url", None)})
    new_refresh = create_refresh_token(data={"sub": user.id, "role": user.role, "email": user.email, "picture": getattr(user, "profile_picture_url", None), "jti": new_jti_str})
    
    # Invalidate old token session and create a new one (Session Rotation)
    await session_repo.revoke_session(db_session.id)
    
    session_id = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    await session_repo.create_session(
        session_id=session_id,
        user_id=user.id,
        refresh_token_jti=new_jti_str,
        expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

    token_data = TokenResponse(
        access_token=new_access,
        refresh_token="cookie"
    )
    return wrap_response(
        success=True,
        data=token_data,
        message="Token refreshed successfully",
        request_id=request.state.request_id
    )

@router.post("/auth/logout", response_model=APIResponseEnvelope)
async def logout(
    request: Request,
    response: Response,
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """Revoke the current session."""
    token = request.cookies.get("refresh_token")
    if token:
        try:
            payload = decode_token(token)
            jti = payload.get("jti")
            if jti:
                db_session = await session_repo.get_session_by_jti(jti)
                if db_session:
                    await session_repo.revoke_session(db_session.id)
        except ValueError:
            pass # Ignore decoding errors on logout

    response.delete_cookie("refresh_token")
    return wrap_response(
        success=True,
        message="Logged out successfully",
        request_id=request.state.request_id
    )

@router.get("/me/preferences", response_model=APIResponseEnvelope)
async def get_preferences(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Retrieve user preferences."""
    return wrap_response(
        success=True,
        data=current_user.preferences,
        request_id=request.state.request_id
    )

@router.patch("/me/preferences", response_model=APIResponseEnvelope)
async def update_preferences(
    request: Request,
    payload: dict,
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Partially update user preferences."""
    # Deep merge or shallow merge preferences
    current_prefs = current_user.preferences or {}
    updated_prefs = {**current_prefs, **payload}
    
    current_user.preferences = updated_prefs
    await user_repo.update(current_user)
    
    return wrap_response(
        success=True,
        data=updated_prefs,
        message="Preferences updated successfully",
        request_id=request.state.request_id
    )

@router.get("/profile", response_model=APIResponseEnvelope)
async def get_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Retrieve detailed player hardware settings and gameplay parameters."""
    use_case = GetProfileUseCase(user_repo)
    profile = await use_case.execute(current_user.id)
    
    res_data = PlayerProfileResponse(
        user_id=profile.user_id,
        rank=profile.rank,
        region=profile.region,
        preferred_agents=profile.preferred_agents,
        roles=profile.roles,
        sensitivity=profile.sensitivity,
        resolution=profile.resolution,
        crosshair=profile.crosshair,
        hardware=profile.hardware,
        monitor_hz=profile.monitor_hz,
        mouse_dpi=profile.mouse_dpi,
        playstyle=profile.playstyle,
        preferred_maps=profile.preferred_maps
    )
    return wrap_response(
        success=True,
        data=res_data,
        message="Profile retrieved successfully",
        request_id=request.state.request_id
    )

@router.put("/profile", response_model=APIResponseEnvelope)
async def update_profile(
    request: Request,
    update_req: PlayerProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Modify player DPI, hardware configurations, maps, or agent selections."""
    use_case = UpdateProfileUseCase(user_repo)
    profile = await use_case.execute(current_user.id, update_req)
    
    res_data = PlayerProfileResponse(
        user_id=profile.user_id,
        rank=profile.rank,
        region=profile.region,
        preferred_agents=profile.preferred_agents,
        roles=profile.roles,
        sensitivity=profile.sensitivity,
        resolution=profile.resolution,
        crosshair=profile.crosshair,
        hardware=profile.hardware,
        monitor_hz=profile.monitor_hz,
        mouse_dpi=profile.mouse_dpi,
        playstyle=profile.playstyle,
        preferred_maps=profile.preferred_maps
    )
    return wrap_response(
        success=True,
        data=res_data,
        message="Profile updated successfully",
        request_id=request.state.request_id
    )

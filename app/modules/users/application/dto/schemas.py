from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class GoogleLoginRequest(BaseModel):
    credential: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class PlayerProfileResponse(BaseModel):
    user_id: str
    rank: Optional[str] = None
    region: Optional[str] = None
    preferred_agents: List[str] = []
    roles: List[str] = []
    sensitivity: Optional[float] = None
    resolution: Optional[str] = None
    crosshair: Optional[str] = None
    hardware: Optional[str] = None
    monitor_hz: Optional[int] = None
    mouse_dpi: Optional[int] = None
    playstyle: Optional[str] = None
    preferred_maps: List[str] = []

class PlayerProfileUpdateRequest(BaseModel):
    rank: Optional[str] = None
    region: Optional[str] = None
    preferred_agents: Optional[List[str]] = None
    roles: Optional[List[str]] = None
    sensitivity: Optional[float] = None
    resolution: Optional[str] = None
    crosshair: Optional[str] = None
    hardware: Optional[str] = None
    monitor_hz: Optional[int] = None
    mouse_dpi: Optional[int] = None
    playstyle: Optional[str] = None
    preferred_maps: Optional[List[str]] = None

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    is_active: bool
    is_verified: bool
    profile: Optional[PlayerProfileResponse] = None
    preferences: dict = {}

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.modules.users.domain.entities.user import User, PlayerProfile
from app.modules.users.domain.repositories.user_repository import UserRepository
from app.modules.users.infrastructure.models.user_table import UserTable
from app.modules.users.infrastructure.models.profile_table import ProfileTable

class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain_profile(self, p_table: ProfileTable) -> PlayerProfile:
        return PlayerProfile(
            user_id=p_table.user_id,
            rank=p_table.rank,
            region=p_table.region,
            preferred_agents=p_table.preferred_agents or [],
            roles=p_table.roles or [],
            sensitivity=p_table.sensitivity,
            resolution=p_table.resolution,
            crosshair=p_table.crosshair,
            hardware=p_table.hardware,
            monitor_hz=p_table.monitor_hz,
            mouse_dpi=p_table.mouse_dpi,
            playstyle=p_table.playstyle,
            preferred_maps=p_table.preferred_maps or []
        )

    def _to_domain_user(self, u_table: UserTable) -> User:
        profile = None
        if u_table.profile:
            profile = self._to_domain_profile(u_table.profile)
        return User(
            id=u_table.id,
            email=u_table.email,
            hashed_password=u_table.hashed_password,
            role=u_table.role,
            is_active=u_table.is_active,
            is_verified=u_table.is_verified,
            google_id=u_table.google_id,
            profile_picture_url=u_table.profile_picture_url,
            created_at=u_table.created_at,
            updated_at=u_table.updated_at,
            profile=profile,
            preferences=u_table.preferences or {}
        )

    async def get_by_id(self, user_id: str) -> Optional[User]:
        stmt = select(UserTable).where(UserTable.id == user_id).options(selectinload(UserTable.profile))
        result = await self.session.execute(stmt)
        u_table = result.scalar_one_or_none()
        if not u_table:
            return None
        return self._to_domain_user(u_table)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(UserTable).where(UserTable.email == email).options(selectinload(UserTable.profile))
        result = await self.session.execute(stmt)
        u_table = result.scalar_one_or_none()
        if not u_table:
            return None
        return self._to_domain_user(u_table)

    async def save(self, user: User) -> User:
        u_table = UserTable(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            google_id=user.google_id,
            profile_picture_url=user.profile_picture_url,
            preferences=user.preferences
        )
        self.session.add(u_table)
        await self.session.flush()
        return user

    async def update(self, user: User) -> User:
        stmt = select(UserTable).where(UserTable.id == user.id)
        result = await self.session.execute(stmt)
        u_table = result.scalar_one_or_none()
        if u_table:
            u_table.email = user.email
            u_table.hashed_password = user.hashed_password
            u_table.role = user.role
            u_table.is_active = user.is_active
            u_table.is_verified = user.is_verified
            u_table.google_id = user.google_id
            u_table.profile_picture_url = user.profile_picture_url
            u_table.preferences = user.preferences
            await self.session.flush()
        return user

    async def get_profile(self, user_id: str) -> Optional[PlayerProfile]:
        stmt = select(ProfileTable).where(ProfileTable.user_id == user_id)
        result = await self.session.execute(stmt)
        p_table = result.scalar_one_or_none()
        if not p_table:
            return None
        return self._to_domain_profile(p_table)

    async def save_profile(self, profile: PlayerProfile) -> PlayerProfile:
        stmt = select(ProfileTable).where(ProfileTable.user_id == profile.user_id)
        result = await self.session.execute(stmt)
        p_table = result.scalar_one_or_none()

        if not p_table:
            p_table = ProfileTable(user_id=profile.user_id)
            self.session.add(p_table)

        p_table.rank = profile.rank
        p_table.region = profile.region
        p_table.preferred_agents = profile.preferred_agents
        p_table.roles = profile.roles
        p_table.sensitivity = profile.sensitivity
        p_table.resolution = profile.resolution
        p_table.crosshair = profile.crosshair
        p_table.hardware = profile.hardware
        p_table.monitor_hz = profile.monitor_hz
        p_table.mouse_dpi = profile.mouse_dpi
        p_table.playstyle = profile.playstyle
        p_table.preferred_maps = profile.preferred_maps

        await self.session.flush()
        return profile

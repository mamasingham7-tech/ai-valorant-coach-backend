from app.modules.users.domain.entities.user import PlayerProfile
from app.modules.users.domain.repositories.user_repository import UserRepository
from app.modules.users.application.dto.schemas import PlayerProfileUpdateRequest
from app.shared.events.event_bus import event_bus, ProfileUpdated

class UpdateProfileUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, user_id: str, request: PlayerProfileUpdateRequest) -> PlayerProfile:
        profile = await self.user_repo.get_profile(user_id)
        if not profile:
            profile = PlayerProfile(user_id=user_id)

        updates = {}
        if request.rank is not None:
            profile.rank = request.rank
            updates["rank"] = request.rank
        if request.region is not None:
            profile.region = request.region
            updates["region"] = request.region
        if request.preferred_agents is not None:
            profile.preferred_agents = request.preferred_agents
            updates["preferred_agents"] = request.preferred_agents
        if request.roles is not None:
            profile.roles = request.roles
            updates["roles"] = request.roles
        if request.sensitivity is not None:
            profile.sensitivity = request.sensitivity
            updates["sensitivity"] = request.sensitivity
        if request.resolution is not None:
            profile.resolution = request.resolution
            updates["resolution"] = request.resolution
        if request.crosshair is not None:
            profile.crosshair = request.crosshair
            updates["crosshair"] = request.crosshair
        if request.hardware is not None:
            profile.hardware = request.hardware
            updates["hardware"] = request.hardware
        if request.monitor_hz is not None:
            profile.monitor_hz = request.monitor_hz
            updates["monitor_hz"] = request.monitor_hz
        if request.mouse_dpi is not None:
            profile.mouse_dpi = request.mouse_dpi
            updates["mouse_dpi"] = request.mouse_dpi
        if request.playstyle is not None:
            profile.playstyle = request.playstyle
            updates["playstyle"] = request.playstyle
        if request.preferred_maps is not None:
            profile.preferred_maps = request.preferred_maps
            updates["preferred_maps"] = request.preferred_maps

        await self.user_repo.save_profile(profile)
        
        if updates:
            # Dispatch event asynchronously
            await event_bus.publish(ProfileUpdated(user_id=user_id, updates=updates))
            
        return profile

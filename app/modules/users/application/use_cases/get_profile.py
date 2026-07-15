from app.modules.users.domain.entities.user import PlayerProfile
from app.modules.users.domain.repositories.user_repository import UserRepository

class GetProfileUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, user_id: str) -> PlayerProfile:
        profile = await self.user_repo.get_profile(user_id)
        if not profile:
            profile = PlayerProfile(user_id=user_id)
            await self.user_repo.save_profile(profile)
        return profile

import pytest
from app.modules.users.application.dto.schemas import PlayerProfileUpdateRequest
from app.modules.users.application.use_cases.get_profile import GetProfileUseCase
from app.modules.users.application.use_cases.update_profile import UpdateProfileUseCase

@pytest.mark.asyncio
async def test_get_and_update_profile(mock_user_repo):
    get_profile = GetProfileUseCase(mock_user_repo)
    update_profile = UpdateProfileUseCase(mock_user_repo)
    
    user_id = "test-user-uuid"
    
    # Get profile (seeds a default profile if none exists)
    profile = await get_profile.execute(user_id)
    assert profile.user_id == user_id
    assert profile.rank is None
    
    # Update profile fields
    update_req = PlayerProfileUpdateRequest(
        rank="Diamond 3",
        region="NA",
        preferred_agents=["Jett", "Omen"],
        sensitivity=0.35,
        mouse_dpi=800
    )
    
    updated_profile = await update_profile.execute(user_id, update_req)
    assert updated_profile.rank == "Diamond 3"
    assert updated_profile.region == "NA"
    assert updated_profile.preferred_agents == ["Jett", "Omen"]
    assert updated_profile.sensitivity == 0.35
    assert updated_profile.mouse_dpi == 800

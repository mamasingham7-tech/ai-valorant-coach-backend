import pytest
from app.modules.users.application.dto.schemas import UserRegisterRequest
from app.modules.users.application.use_cases.register_user import RegisterUserUseCase

@pytest.mark.asyncio
async def test_register_user_success(mock_user_repo):
    use_case = RegisterUserUseCase(mock_user_repo)
    request = UserRegisterRequest(email="test@example.com", password="password123")
    
    user = await use_case.execute(request)
    assert user.email == "test@example.com"
    assert user.is_active is True
    assert user.is_verified is False
    assert user.profile is not None
    
    # Assert duplicate registration raises error
    with pytest.raises(ValueError, match="Email already registered"):
        await use_case.execute(request)

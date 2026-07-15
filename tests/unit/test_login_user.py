import pytest
from app.modules.users.application.dto.schemas import UserLoginRequest, UserRegisterRequest
from app.modules.users.application.use_cases.register_user import RegisterUserUseCase
from app.modules.users.application.use_cases.login_user import LoginUserUseCase

@pytest.mark.asyncio
async def test_login_user_success(mock_user_repo):
    register_use_case = RegisterUserUseCase(mock_user_repo)
    login_use_case = LoginUserUseCase(mock_user_repo)
    
    # Register user
    await register_use_case.execute(
        UserRegisterRequest(email="login_test@example.com", password="securepassword123")
    )
    
    # Successful Login
    user = await login_use_case.execute(
        UserLoginRequest(email="login_test@example.com", password="securepassword123")
    )
    assert user.email == "login_test@example.com"

@pytest.mark.asyncio
async def test_login_user_failures(mock_user_repo):
    register_use_case = RegisterUserUseCase(mock_user_repo)
    login_use_case = LoginUserUseCase(mock_user_repo)
    
    await register_use_case.execute(
        UserRegisterRequest(email="fail_test@example.com", password="securepassword123")
    )
    
    # Fail email mismatch
    with pytest.raises(ValueError, match="Invalid email or password"):
        await login_use_case.execute(
            UserLoginRequest(email="wrong@example.com", password="securepassword123")
        )

    # Fail password mismatch
    with pytest.raises(ValueError, match="Invalid email or password"):
        await login_use_case.execute(
            UserLoginRequest(email="fail_test@example.com", password="wrongpassword")
        )

    # Fail deactivated user
    user = await mock_user_repo.get_by_email("fail_test@example.com")
    user.is_active = False
    await mock_user_repo.update(user)
    
    with pytest.raises(ValueError, match="User account is deactivated"):
        await login_use_case.execute(
            UserLoginRequest(email="fail_test@example.com", password="securepassword123")
        )

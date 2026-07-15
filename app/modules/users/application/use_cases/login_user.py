from app.modules.users.domain.entities.user import User
from app.modules.users.domain.repositories.user_repository import UserRepository
from app.modules.users.application.dto.schemas import UserLoginRequest
from app.shared.security.tokens import verify_password
from app.shared.events.event_bus import event_bus, UserLoggedIn

class LoginUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, request: UserLoginRequest) -> User:
        user = await self.user_repo.get_by_email(request.email)
        if not user:
            raise ValueError("Invalid email or password")
            
        if not user.is_active:
            raise ValueError("User account is deactivated")

        if not verify_password(request.password, user.hashed_password):
            raise ValueError("Invalid email or password")

        # Dispatch event asynchronously
        await event_bus.publish(UserLoggedIn(user_id=user.id, email=user.email))
        return user

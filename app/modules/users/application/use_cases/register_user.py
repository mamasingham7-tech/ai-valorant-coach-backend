import uuid
from app.modules.users.domain.entities.user import User, PlayerProfile
from app.modules.users.domain.entities.role import Role
from app.core.config import settings
from app.modules.users.domain.repositories.user_repository import UserRepository
from app.modules.users.application.dto.schemas import UserRegisterRequest
from app.shared.security.tokens import hash_password
from app.shared.events.event_bus import event_bus, UserRegistered

class RegisterUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, request: UserRegisterRequest) -> User:
        existing_user = await self.user_repo.get_by_email(request.email)
        if existing_user:
            raise ValueError("Email already registered")

        user_id = str(uuid.uuid4())
        hashed_pwd = hash_password(request.password)
        role = Role.ADMIN.value if request.email.lower() == settings.ADMIN_EMAIL.lower() else Role.USER.value

        user = User(
            id=user_id,
            email=request.email,
            hashed_password=hashed_pwd,
            role=role,
            is_active=True,
            is_verified=False
        )
        
        await self.user_repo.save(user)
        
        # Initialize default profile settings
        profile = PlayerProfile(user_id=user_id)
        await self.user_repo.save_profile(profile)
        user.profile = profile
        
        # Dispatch event asynchronously
        await event_bus.publish(UserRegistered(user_id=user_id, email=request.email))
        
        return user

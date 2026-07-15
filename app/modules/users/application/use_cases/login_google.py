import os
import uuid
from google.oauth2 import id_token
from google.auth.transport import requests
from app.modules.users.domain.entities.user import User
from app.modules.users.domain.repositories.user_repository import UserRepository
from app.modules.users.application.dto.schemas import GoogleLoginRequest
from app.shared.events.event_bus import event_bus, UserLoggedIn, UserRegistered

class LoginGoogleUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, request: GoogleLoginRequest) -> User:
        client_id = os.environ.get("GOOGLE_CLIENT_ID")
        if not client_id:
            raise ValueError("Google authentication is not configured on the server.")

        try:
            # Verify the token against Google's servers
            idinfo = id_token.verify_oauth2_token(
                request.credential, requests.Request(), client_id
            )

            # Check if this token was issued for our client
            if idinfo['aud'] != client_id:
                raise ValueError("Could not verify audience.")

            email = idinfo.get('email')
            google_id = idinfo.get('sub')
            picture = idinfo.get('picture')

            if not email or not google_id:
                raise ValueError("Invalid Google token payload. Missing email or sub.")

            # Check if user already exists
            user = await self.user_repo.get_by_email(email)
            if user:
                # Link account if not already linked
                updated = False
                if not user.google_id:
                    user.google_id = google_id
                    updated = True
                
                # Optionally sync profile picture if they didn't have one
                if picture and not user.profile_picture_url:
                    user.profile_picture_url = picture
                    updated = True
                
                # Ensure they are marked verified
                if not user.is_verified:
                    user.is_verified = True
                    updated = True

                if updated:
                    await self.user_repo.update(user)
                
                if not user.is_active:
                    raise ValueError("User account is deactivated")

                await event_bus.publish(UserLoggedIn(user_id=user.id, email=user.email))
                return user
            
            # Create a new user securely
            new_user = User(
                id=str(uuid.uuid4()),
                email=email,
                hashed_password="!GOOGLE_AUTH", # Impossible hash, prevents password login
                role="user",
                is_active=True,
                is_verified=True,
                google_id=google_id,
                profile_picture_url=picture
            )

            saved_user = await self.user_repo.save(new_user)
            
            await event_bus.publish(UserRegistered(user_id=saved_user.id, email=saved_user.email))
            await event_bus.publish(UserLoggedIn(user_id=saved_user.id, email=saved_user.email))
            
            return saved_user

        except ValueError as e:
            # Re-raise our own ValueErrors
            if "Google authentication" in str(e) or "User account is deactivated" in str(e):
                raise e
            # Catch token validation errors
            raise ValueError(f"Invalid Google token: {str(e)}")

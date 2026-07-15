import redis
import json
import hashlib
from typing import Optional, Dict, Any
import structlog
from app.core.config import settings

logger = structlog.get_logger()

class RedisClient:
    def __init__(self):
        self.url = settings.REDIS_URL
        self._fallback_store: Dict[str, str] = {}
        self.client = None
        self.is_connected = False
        self._connect()

    def _connect(self) -> None:
        try:
            self.client = redis.from_url(self.url, decode_responses=True, socket_connect_timeout=2)
            self.client.ping()
            self.is_connected = True
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.warning("Redis is offline, operating with in-memory fallback store", error=str(e))
            self.client = None
            self.is_connected = False

    def ping(self) -> bool:
        """Verify Redis connectivity."""
        if not self.is_connected or not self.client:
            return False
        try:
            return self.client.ping()
        except Exception:
            return False

    def get(self, key: str) -> Optional[str]:
        if self.is_connected and self.client:
            try:
                return self.client.get(key)
            except Exception as e:
                logger.error("Redis connection error during GET", error=str(e))
        return self._fallback_store.get(key)

    def setex(self, key: str, seconds: int, value: str) -> None:
        if self.is_connected and self.client:
            try:
                self.client.setex(key, seconds, value)
                return
            except Exception as e:
                logger.error("Redis connection error during SETEX", error=str(e))
        self._fallback_store[key] = value

    def delete(self, key: str) -> None:
        if self.is_connected and self.client:
            try:
                self.client.delete(key)
                return
            except Exception as e:
                logger.error("Redis connection error during DELETE", error=str(e))
        self._fallback_store.pop(key, None)

# Global Client Instance
redis_client = RedisClient()

# Token Rotation Helpers
def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def register_refresh_token(user_id: str, token: str, family_id: str, expires_in_seconds: int) -> None:
    token_hash = hash_token(token)
    payload = json.dumps({
        "user_id": user_id,
        "family_id": family_id,
        "revoked": False
    })
    # Store token status
    redis_client.setex(f"rt:token:{token_hash}", expires_in_seconds, payload)

def verify_and_rotate_token(token: str) -> tuple[str, str]:
    """
    Validates token rotation. Returns (user_id, family_id) if valid.
    Raises ValueError for reuse/theft detection.
    """
    token_hash = hash_token(token)
    data_str = redis_client.get(f"rt:token:{token_hash}")
    
    if not data_str:
         raise ValueError("Invalid refresh token")
         
    data = json.loads(data_str)
    family_id = data["family_id"]
    user_id = data["user_id"]
    
    # Check if family is already marked revoked
    if redis_client.get(f"rt:family:{family_id}:revoked") == "true":
        raise ValueError("Token family revoked (reuse breach)")
        
    # Reuse detection: if this token was already marked revoked
    if data["revoked"]:
        # Block the family immediately to prevent breach propagation
        redis_client.setex(f"rt:family:{family_id}:revoked", 86400 * 7, "true")
        raise ValueError("Token reuse detected, entire family revoked")
        
    # Mark old token as revoked (used)
    data["revoked"] = True
    # Keep it in storage to catch potential reuses
    redis_client.setex(f"rt:token:{token_hash}", 86400 * 7, json.dumps(data))
    
    return user_id, family_id


def revoke_token_family(token: str) -> None:
    """Revokes the token family associated with a refresh token (e.g. on logout)."""
    token_hash = hash_token(token)
    data_str = redis_client.get(f"rt:token:{token_hash}")
    if data_str:
        data = json.loads(data_str)
        family_id = data["family_id"]
        redis_client.setex(f"rt:family:{family_id}:revoked", 86400 * 7, "true")

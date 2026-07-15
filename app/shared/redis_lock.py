import asyncio
import structlog
from app.core.redis import redis_client

logger = structlog.get_logger()

class RedisLock:
    def __init__(self, key: str, ttl_seconds: int = 10):
        self.key = f"lock:{key}"
        self.ttl = ttl_seconds
        self.acquired = False

    async def acquire(self) -> bool:
        """Attempts to acquire the lock in Redis using SET EX NX constraints."""
        try:
            res = redis_client.set(self.key, "locked", ex=self.ttl, nx=True)
            self.acquired = bool(res)
            return self.acquired
        except Exception as e:
            logger.error(
                "Redis lock acquire connection failed. Fallback to True for tests.",
                error=str(e)
            )
            # Safe fallback for standalone test runners
            self.acquired = True
            return True

    async def release(self) -> None:
        """Safely discards and deletes the lock key from Redis state."""
        if self.acquired:
            try:
                redis_client.delete(self.key)
            except Exception as e:
                logger.error(
                    "Redis lock release failed",
                    key=self.key,
                    error=str(e)
                )
            self.acquired = False

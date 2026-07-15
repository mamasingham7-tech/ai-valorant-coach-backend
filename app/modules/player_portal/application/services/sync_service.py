import uuid
import json
import dataclasses
import structlog
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.modules.player_portal.application.providers.base import IValorantProvider
from app.modules.player_portal.domain.entities import RiotAccount
from app.core.redis import redis_client

logger = structlog.get_logger()

ACCOUNT_CACHE_TTL = 300   # 5 minutes
RANK_CACHE_TTL    = 900   # 15 minutes
MATCH_CACHE_TTL   = 900   # 15 minutes

class SyncService:
    """Orchestrates data fetching, caching, and synchronisation via any IValorantProvider."""

    def __init__(self, provider: IValorantProvider):
        self.provider = provider

    # ── Cache key helpers ────────────────────────────────────────────────────

    def _key_account(self, game_name: str, tag: str) -> str:
        return f"portal:account:{game_name.lower()}:{tag.lower()}"

    def _key_rank(self, game_name: str, tag: str, region: str) -> str:
        return f"portal:rank:{region}:{game_name.lower()}:{tag.lower()}"

    def _key_matches(self, game_name: str, tag: str, region: str, mode: str) -> str:
        return f"portal:matches:{region}:{mode}:{game_name.lower()}:{tag.lower()}"

    # ── Public methods ───────────────────────────────────────────────────────

    async def link_account(self, user_id: str, game_name: str, tag_line: str) -> Optional[RiotAccount]:
        """Verify Riot ID exists via provider and return an enriched RiotAccount entity."""
        logger.info("Linking Riot account", user_id=user_id, game_name=game_name, tag_line=tag_line, provider=self.provider.provider_name)

        # Try cache first
        cached_str = redis_client.get(self._key_account(game_name, tag_line))
        if cached_str:
            try:
                data = json.loads(cached_str)
                account = RiotAccount(**{k: v for k, v in data.items() if k in RiotAccount.__dataclass_fields__})
                account.user_id = user_id
                logger.info("Account served from cache")
                return account
            except Exception:
                pass  # Cache miss — proceed to live fetch

        account = await self.provider.get_account(game_name, tag_line)
        if not account:
            return None

        account.id = str(uuid.uuid4())
        account.user_id = user_id
        account.last_sync = datetime.utcnow()

        # Persist to cache
        cache_data = {
            "id": account.id,
            "user_id": account.user_id,
            "game_name": account.game_name,
            "tag_line": account.tag_line,
            "puuid": account.puuid,
            "region": account.region,
            "account_level": account.account_level,
            "is_verified": account.is_verified,
            "last_sync": account.last_sync.isoformat() if account.last_sync else None,
            "provider": account.provider,
            "created_at": None,
        }
        redis_client.setex(self._key_account(game_name, tag_line), ACCOUNT_CACHE_TTL, json.dumps(cache_data))
        return account

    async def get_rank(self, game_name: str, tag_line: str, region: str) -> Optional[Dict[str, Any]]:
        """Fetch and cache rank data for a player."""
        cached = redis_client.get(self._key_rank(game_name, tag_line, region))
        if cached:
            return json.loads(cached)

        rank = await self.provider.get_rank(game_name, tag_line, region)
        if not rank:
            return None

        result = dataclasses.asdict(rank)
        redis_client.setex(self._key_rank(game_name, tag_line, region), RANK_CACHE_TTL, json.dumps(result))
        return result

    async def get_matches(
        self, game_name: str, tag_line: str, region: str,
        mode: str = "competitive", size: int = 20
    ) -> List[Dict[str, Any]]:
        """Fetch and cache match history for a player."""
        cached = redis_client.get(self._key_matches(game_name, tag_line, region, mode))
        if cached:
            return json.loads(cached)

        matches = await self.provider.get_match_history(game_name, tag_line, region, mode, size)
        result = [dataclasses.asdict(m) for m in matches]
        if result:
            redis_client.setex(self._key_matches(game_name, tag_line, region, mode), MATCH_CACHE_TTL, json.dumps(result))
        return result

import structlog
from app.core.config import settings
from app.modules.player_portal.application.providers.base import IValorantProvider
from app.modules.player_portal.application.providers.henrikdev_provider import HenrikDevProvider
from app.modules.player_portal.application.providers.mock_provider import MockProvider

logger = structlog.get_logger()

def get_valorant_provider() -> IValorantProvider:
    """Provider factory. Reads from pydantic settings (not raw os.getenv).

    Priority:
    1. MockProvider       — if USE_MOCK_PROVIDER=true  (development/demo, instant data)
    2. HenrikDevProvider  — if HENRIK_API_KEY is set (real data, free key from henrikdev.xyz)
    3. HenrikDevProvider  — default fallback (will fail with 401 if HenrikDev now requires a key)
    """
    # Always use pydantic settings — not os.getenv — so the value is consistent
    if settings.USE_MOCK_PROVIDER:
        logger.info("Valorant provider: MockProvider (USE_MOCK_PROVIDER=true)")
        return MockProvider()

    # Check for HenrikDev API key
    henrik_key = getattr(settings, "HENRIK_API_KEY", "") or ""
    logger.info(
        "Valorant provider: HenrikDevProvider",
        has_api_key=bool(henrik_key),
    )
    return HenrikDevProvider(api_key=henrik_key if henrik_key else None)

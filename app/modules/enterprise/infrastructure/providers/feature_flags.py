import structlog
from typing import Dict, Any

logger = structlog.get_logger()

class FeatureFlagsManager:
    def __init__(self):
        # Default flag registry values for fallback
        self._flags = {
            "realtime_coaching_enabled": True,
            "shadow_mlops_enabled": True,
            "dynamic_drills_enabled": False
        }

    def is_enabled(self, flag: str, user_id: str = "", role: str = "") -> bool:
        """Determines if the feature flag is enabled for the context user or role."""
        # 1. Role overrides (ADMIN always gets features unlocked)
        if role == "ADMIN":
            return True
            
        # 2. Percentage rollout filters based on user hash keys
        if user_id:
            user_hash = hash(user_id) % 100
            if flag == "dynamic_drills_enabled" and user_hash < 25:
                return True
                
        return self._flags.get(flag, False)

from typing import Dict
from app.modules.ai.domain.entities.capability import AICapability

class CapabilityRegistry:
    def __init__(self):
        self._capabilities: Dict[str, AICapability] = {}

    def register(self, capability: AICapability) -> None:
        self._capabilities[capability.name] = capability

    def get(self, name: str) -> AICapability:
        cap = self._capabilities.get(name)
        if not cap:
            raise ValueError(f"Capability '{name}' is not registered.")
        return cap

# Global Registry Instance
capability_registry = CapabilityRegistry()

# Import default capabilities to trigger self-registration
import app.modules.ai.infrastructure.registry.default_capabilities

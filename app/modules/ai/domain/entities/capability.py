from abc import ABC, abstractmethod
from typing import Dict, Any

class AICapability(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """The identifier name of the capability."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Semantic version of the capability configuration."""
        pass

    @abstractmethod
    async def execute(self, context: Dict[str, Any], provider: Any) -> Dict[str, Any]:
        """Executes the specific prompt generation logic using the provided model provider."""
        pass

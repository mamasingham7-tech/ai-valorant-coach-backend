from abc import ABC, abstractmethod
from typing import Dict, Any

class ModelProvider(ABC):
    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        system_prompt: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sends context to the model provider.
        Returns a normalized dictionary containing:
        - provider (str)
        - model_version (str)
        - response (str)
        - latency_ms (int)
        - token_usage (dict)
        """
        pass

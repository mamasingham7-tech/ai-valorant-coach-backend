import time
import structlog
from typing import Dict, Any
from app.modules.ai.domain.interfaces.model_provider import ModelProvider

logger = structlog.get_logger()

class LocalProvider(ModelProvider):
    def __init__(self, model_version: str = "llama-3-8b-instruct"):
        self.model_version = model_version

    async def generate_response(
        self,
        prompt: str,
        system_prompt: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        start_time = time.perf_counter()
        
        response_text = (
            f"Local Llama Mock Response:\n"
            f"Evaluated save round vs forced buy thresholds.\n"
            f"Suggests eco economy prioritization."
        )
        
        latency_ms = int((time.perf_counter() - start_time) * 1000)
        
        return {
            "provider": "local",
            "model_version": self.model_version,
            "response": response_text,
            "latency_ms": latency_ms,
            "confidence": 0.90,
            "token_usage": {
                "prompt_tokens": 90,
                "completion_tokens": 45,
                "total_tokens": 135
            }
        }

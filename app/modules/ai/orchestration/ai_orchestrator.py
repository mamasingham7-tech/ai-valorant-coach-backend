import time
import structlog
from typing import Dict, Any
from app.modules.ai.infrastructure.registry.capability_registry import capability_registry
from app.modules.ai.orchestration.context_builder import AIContextBuilder
from app.modules.ai.domain.interfaces.model_provider import ModelProvider

logger = structlog.get_logger()

class AIOrchestrator:
    def __init__(self, provider: ModelProvider):
        self.provider = provider
        self.context_builder = AIContextBuilder()

    async def execute_capability(
        self,
        capability_name: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Orchestrates request flows: retrieves capabilities, builds unified contexts,
        dispatches calls to model adapters, and normalizes output mappings.
        """
        request_id = input_data.get("request_id", "")
        correlation_id = input_data.get("correlation_id", "")
        
        start_time = time.perf_counter()
        
        logger.info(
            "Executing AI capability",
            capability=capability_name,
            provider=self.provider.__class__.__name__,
            request_id=request_id,
            correlation_id=correlation_id
        )
        
        # 1. Resolve capability
        capability = capability_registry.get(capability_name)
        
        # 2. Build context
        context = await self.context_builder.build_context(
            profile=input_data.get("profile", {}),
            dna=input_data.get("dna", {}),
            analytics=input_data.get("analytics", {}),
            recommendations=input_data.get("recommendations", {}),
            memory=input_data.get("memory", {}),
            session=input_data.get("session", {}),
            versions={
                "prompt_version": input_data.get("prompt_version", "1.0.0"),
                "feature_version": input_data.get("feature_version", "1.0.0"),
                "analytics_version": input_data.get("analytics_version", "1.0.0"),
                "model_version": getattr(self.provider, "model_version", "1.0.0")
            }
        )
        
        # 3. Execute capability with model provider
        result = await capability.execute(context, self.provider)
        
        latency_ms = int((time.perf_counter() - start_time) * 1000)
        
        # 4. Normalize output structure
        normalized_response = {
            "success": True,
            "capability": capability_name,
            "version": capability.version,
            "provider": result.get("provider"),
            "confidence": result.get("confidence", 0.95),
            "metadata": {
                "model_version": result.get("model_version"),
                "prompt_version": context["versions"]["prompt_version"],
                "feature_version": context["versions"]["feature_version"],
                "analytics_version": context["versions"]["analytics_version"],
                "latency_ms": latency_ms,
                "token_usage": result.get("token_usage", {}),
                "request_id": request_id,
                "correlation_id": correlation_id
            },
            "response": result.get("response")
        }
        
        logger.info(
            "AI capability execution complete",
            capability=capability_name,
            latency_ms=latency_ms,
            tokens=result.get("token_usage"),
            request_id=request_id,
            correlation_id=correlation_id
        )
        
        return normalized_response

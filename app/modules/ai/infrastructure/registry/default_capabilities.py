from typing import Dict, Any
from app.modules.ai.domain.entities.capability import AICapability
from app.modules.ai.infrastructure.registry.capability_registry import capability_registry
from app.modules.ai.infrastructure.prompts.prompt_repository import PromptRepository

prompt_repo = PromptRepository()

class BaseCapability(AICapability):
    def __init__(self, name: str, version: str = "1.0.0"):
        self._name = name
        self._version = version

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    async def execute(self, context: Dict[str, Any], provider: Any) -> Dict[str, Any]:
        prompt_template = prompt_repo.get_prompt(self._name)
        # Safely format template with context dictionary
        prompt = prompt_template.format(context=context)
        system_prompt = f"You are an AI platform agent executing capability {self._name}."
        return await provider.generate_response(prompt, system_prompt, context)

def register_default_capabilities():
    defaults = [
        "analytics_summary",
        "chat_coach",
        "training_generator",
        "match_summary",
        "habit_explainer",
        "vod_review"
    ]
    for name in defaults:
        # Check if already registered to avoid duplication
        try:
            capability_registry.get(name)
        except ValueError:
            capability_registry.register(BaseCapability(name))

# Register default capabilities automatically
register_default_capabilities()

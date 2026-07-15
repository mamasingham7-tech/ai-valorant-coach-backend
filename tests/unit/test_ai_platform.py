import pytest
from app.modules.ai.infrastructure.registry.capability_registry import capability_registry
from app.modules.ai.infrastructure.prompts.prompt_repository import PromptRepository
from app.modules.ai.infrastructure.memory.coach_memory_repository import SQLAlchemyCoachMemoryRepository
from app.modules.ai.domain.entities.coach_memory import CoachMemory
from app.modules.ai.infrastructure.providers.openai_provider import OpenAIProvider
from app.modules.ai.infrastructure.providers.anthropic_provider import AnthropicProvider
from app.modules.ai.infrastructure.providers.gemini_provider import GeminiProvider
from app.modules.ai.infrastructure.providers.local_provider import LocalProvider
from app.modules.ai.orchestration.context_builder import AIContextBuilder
from app.modules.ai.orchestration.ai_orchestrator import AIOrchestrator

@pytest.mark.asyncio
async def test_capability_registry():
    # 1. Test fetching registered defaults
    analytics_cap = capability_registry.get("analytics_summary")
    assert analytics_cap.name == "analytics_summary"
    assert analytics_cap.version == "1.0.0"

    # 2. Test error thrown for unregistered lookup
    with pytest.raises(ValueError, match="Capability 'invalid_name' is not registered"):
        capability_registry.get("invalid_name")


def test_prompt_repository():
    repo = PromptRepository()
    
    # Verify templates mapped
    template = repo.get_prompt("analytics_summary")
    assert "Ratings: {context[analytics][ratings]}" in template
    
    # Verify version mappings
    version = repo.get_version("analytics_summary")
    assert version == "1.0.0"

    with pytest.raises(KeyError):
        repo.get_prompt("invalid_key")


@pytest.mark.asyncio
async def test_coach_memory_repository():
    repo = SQLAlchemyCoachMemoryRepository()  # Defaults to in-memory fallback
    
    # 1. Fetch default blank state
    memory = await repo.get_by_user_id("user-111")
    assert memory.user_id == "user-111"
    assert len(memory.recurring_habits) == 0

    # 2. Save mutated states
    memory.recurring_habits = ["panic-crouch"]
    memory.player_dna = {"playstyle": "AGGRESSIVE"}
    await repo.save(memory)
    
    # 3. Reload and check state persistence
    reloaded = await repo.get_by_user_id("user-111")
    assert reloaded.recurring_habits == ["panic-crouch"]
    assert reloaded.player_dna == {"playstyle": "AGGRESSIVE"}


@pytest.mark.asyncio
async def test_context_builder():
    builder = AIContextBuilder()
    context = await builder.build_context(
        profile={"user_id": "user-1", "rank": "Gold 3"},
        dna={"playstyle": "LURKER"},
        analytics={"ratings": {"mechanical": 80}},
        recommendations={"drill": "burst"},
        memory={"streaks": {"win": 2}},
        session={"fatigue": 0.1},
        versions={"model": "gpt-4"}
    )
    
    assert context["profile"]["rank"] == "Gold 3"
    assert context["dna"]["playstyle"] == "LURKER"
    assert context["analytics"]["ratings"]["mechanical"] == 80
    assert context["versions"]["model"] == "gpt-4"


@pytest.mark.asyncio
async def test_providers_stubs():
    # Verify all providers return normalized model response mappings
    openai = OpenAIProvider()
    resp_o = await openai.generate_response("test prompt", "system", {})
    assert resp_o["provider"] == "openai"
    assert "token_usage" in resp_o
    assert resp_o["latency_ms"] >= 0

    anthropic = AnthropicProvider()
    resp_a = await anthropic.generate_response("test prompt", "system", {})
    assert resp_a["provider"] == "anthropic"

    gemini = GeminiProvider()
    resp_g = await gemini.generate_response("test prompt", "system", {})
    assert resp_g["provider"] == "gemini"

    local = LocalProvider()
    resp_l = await local.generate_response("test prompt", "system", {})
    assert resp_l["provider"] == "local"


@pytest.mark.asyncio
async def test_ai_orchestrator_execution():
    provider = OpenAIProvider(model_version="gpt-4-test")
    orchestrator = AIOrchestrator(provider)
    
    input_payload = {
        "request_id": "req-xyz",
        "correlation_id": "corr-123",
        "profile": {"user_id": "user-123", "rank": "Gold 3"},
        "dna": {"playstyle": "AGGRESSIVE"},
        "analytics": {
            "ratings": "82",
            "habits": ["reload-after-kill"],
            "weaknesses": ["crouch-spray"]
        },
        "recommendations": {"drill": "burst-strafing"},
        "memory": {"goal_history": "reach platinum"},
        "session": {"fatigue": 0.2},
        "prompt_version": "1.2.0",
        "feature_version": "1.1.0",
        "analytics_version": "1.0.0"
    }

    # Execute capability execution pipeline
    res = await orchestrator.execute_capability("analytics_summary", input_payload)
    
    # Assert normalized envelope checks
    assert res["success"] is True
    assert res["capability"] == "analytics_summary"
    assert res["provider"] == "openai"
    assert res["confidence"] == 0.96
    
    # Assert version metrics
    metadata = res["metadata"]
    assert metadata["model_version"] == "gpt-4-test"
    assert metadata["prompt_version"] == "1.2.0"
    assert metadata["request_id"] == "req-xyz"
    assert metadata["correlation_id"] == "corr-123"
    assert "token_usage" in metadata
    assert "latency_ms" in metadata
    
    # Assert mock response is returned
    assert "OpenAI Mock Response" in res["response"]

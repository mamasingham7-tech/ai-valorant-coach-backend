from typing import Dict

class PromptRepository:
    def __init__(self):
        # Maps capability keywords to versioned text templates
        self._prompts: Dict[str, str] = {
            "analytics_summary": (
                "Review the following match analytics summary:\n"
                "Ratings: {context[analytics][ratings]}\n"
                "Habits: {context[analytics][habits]}\n"
                "What is the priority coaching focus?"
            ),
            "chat_coach": (
                "You are an AI Valorant Coach chat session assistant.\n"
                "User profile: {context[profile]}\n"
                "Player DNA: {context[dna]}\n"
                "Active Recommendations: {context[recommendations]}\n"
                "How should they handle their next competitive queue?"
            ),
            "training_generator": (
                "Create a structured training routine drill for the player.\n"
                "Weaknesses: {context[analytics][weaknesses]}\n"
                "Practice goals: {context[memory][goal_history]}"
            ),
            "match_summary": (
                "Reconstruct the timeline logs for this match:\n"
                "Matches detail: {context[analytics]}"
            ),
            "habit_explainer": (
                "Provide an in-depth root cause explanation for the following habits:\n"
                "Habits: {context[analytics][habits]}"
            ),
            "vod_review": (
                "Analyze the timeline sequence for this visual execution play:\n"
                "Events: {context[analytics]}"
            )
        }
        self._versions: Dict[str, str] = {
            "analytics_summary": "1.0.0",
            "chat_coach": "1.0.0",
            "training_generator": "1.0.0",
            "match_summary": "1.0.0",
            "habit_explainer": "1.0.0",
            "vod_review": "1.0.0"
        }

    def get_prompt(self, key: str) -> str:
        if key not in self._prompts:
            raise KeyError(f"Prompt template key '{key}' not found in registry.")
        return self._prompts[key]

    def get_version(self, key: str) -> str:
        return self._versions.get(key, "1.0.0")

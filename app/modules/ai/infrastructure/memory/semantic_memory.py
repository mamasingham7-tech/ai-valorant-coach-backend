from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime

@dataclass
class WorkingMemory:
    """Active session parameters, current match details, and recent round decisions."""
    session_id: str
    active_match_id: Optional[str] = None
    recent_decisions: List[Dict[str, Any]] = field(default_factory=list)
    fatigue_index: float = 0.0
    tilt_detected: bool = False

@dataclass
class EpisodicMemory:
    """Historical coaching session logs, match summaries, and previous recommendations."""
    recent_matches: List[Dict[str, Any]] = field(default_factory=list)
    previous_recommendations: List[Dict[str, Any]] = field(default_factory=list)
    drill_completion_history: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class SemanticMemory:
    """Generalized player traits, career progression paths, and persistent player DNA."""
    user_id: str
    player_dna: Dict[str, Any] = field(default_factory=dict)
    stable_habits: List[str] = field(default_factory=list)
    skill_progression: Dict[str, Any] = field(default_factory=dict)
    resolved_weaknesses: List[str] = field(default_factory=list)

class AIPlatformMemoryManager:
    """Orchestrates short-term (working), mid-term (episodic), and long-term (semantic) memory loads."""
    def __init__(self):
        self.working_memories: Dict[str, WorkingMemory] = {}
        self.episodic_memories: Dict[str, EpisodicMemory] = {}
        self.semantic_memories: Dict[str, SemanticMemory] = {}

    def get_working_memory(self, session_id: str) -> WorkingMemory:
        if session_id not in self.working_memories:
            self.working_memories[session_id] = WorkingMemory(session_id=session_id)
        return self.working_memories[session_id]

    def get_episodic_memory(self, user_id: str) -> EpisodicMemory:
        if user_id not in self.episodic_memories:
            self.episodic_memories[user_id] = EpisodicMemory()
        return self.episodic_memories[user_id]

    def get_semantic_memory(self, user_id: str) -> SemanticMemory:
        if user_id not in self.semantic_memories:
            self.semantic_memories[user_id] = SemanticMemory(user_id=user_id)
        return self.semantic_memories[user_id]

    def merge_contexts(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """Binds working, episodic, and semantic layers into a unified memory context."""
        wm = self.get_working_memory(session_id)
        em = self.get_episodic_memory(user_id)
        sm = self.get_semantic_memory(user_id)
        
        return {
            "working_memory": {
                "active_match_id": wm.active_match_id,
                "recent_decisions": wm.recent_decisions,
                "fatigue_index": wm.fatigue_index,
                "tilt_detected": wm.tilt_detected
            },
            "episodic_memory": {
                "recent_matches": em.recent_matches,
                "previous_recommendations": em.previous_recommendations,
                "drill_completion_history": em.drill_completion_history
            },
            "semantic_memory": {
                "player_dna": sm.player_dna,
                "stable_habits": sm.stable_habits,
                "skill_progression": sm.skill_progression,
                "resolved_weaknesses": sm.resolved_weaknesses
            }
        }
from typing import Optional

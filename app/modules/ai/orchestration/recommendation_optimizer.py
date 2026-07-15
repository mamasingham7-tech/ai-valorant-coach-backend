from typing import List, Dict, Any

class RecommendationOptimizer:
    def __init__(self, drills_library: Dict[str, Dict[str, Any]]):
        self.library = drills_library

    def optimize_drills(
        self,
        weaknesses: List[str],
        resolved_habits: List[str],
        player_rank: str,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Ranks drills based on player weaknesses, resolved habits, and rank,
        filtering out drills related to resolved habits to avoid duplicates.
        """
        scored_drills = []
        
        for drill_id, config in self.library.items():
            related_habit = config.get("related_habit")
            if related_habit in resolved_habits:
                continue
                
            score = 0.0
            
            # Match weaknesses
            if related_habit in weaknesses:
                score += 10.0
                
            # Align rank difficulty
            skill_level = config.get("skill_level", "BEGINNER")
            if "immortal" in player_rank.lower() and skill_level == "ADVANCED":
                score += 5.0
            elif "gold" in player_rank.lower() and skill_level == "INTERMEDIATE":
                score += 5.0
            elif skill_level == "BEGINNER":
                score += 2.0
                
            scored_drills.append({
                "drill_id": drill_id,
                "score": score,
                "config": config
            })
            
        # Sort drills by score descending
        scored_drills.sort(key=lambda x: x["score"], reverse=True)
        return [item["config"] for item in scored_drills[:limit]]

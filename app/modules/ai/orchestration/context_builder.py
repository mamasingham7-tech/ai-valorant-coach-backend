from typing import Dict, Any

class AIContextBuilder:
    async def build_context(
        self,
        profile: Dict[str, Any],
        dna: Dict[str, Any],
        analytics: Dict[str, Any],
        recommendations: Dict[str, Any],
        memory: Dict[str, Any],
        session: Dict[str, Any],
        versions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assembles all parameters into one normalized dictionary.
        Returns keys:
        - profile: {}
        - dna: {}
        - analytics: {}
        - recommendations: {}
        - memory: {}
        - session: {}
        - versions: {}
        """
        return {
            "profile": profile,
            "dna": dna,
            "analytics": analytics,
            "recommendations": recommendations,
            "memory": memory,
            "session": session,
            "versions": versions
        }

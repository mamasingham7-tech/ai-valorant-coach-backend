import uuid
import structlog
from typing import Dict, Any, List
from app.modules.live_coaching.domain.entities.live_session import LiveSession, SessionState
from app.modules.live_coaching.infrastructure.websocket.websocket_manager import ws_manager

logger = structlog.get_logger()

class IncrementalAnalyticsEngine:
    def calculate_rolling_fatigue(self, round_num: int, recent_missed_shots: int = 0) -> float:
        """Determines fatigue scale by round progression and recent aim misses."""
        return min(1.0, round_num * 0.04 + recent_missed_shots * 0.05)

    def calculate_win_probability(self, allies_alive: int, enemies_alive: int, credits_delta: int) -> float:
        """Evaluates situational live win probability based on remaining players and credit parity."""
        prob = 0.5 + 0.08 * (allies_alive - enemies_alive) + (credits_delta / 10000) * 0.1
        return max(0.01, min(0.99, prob))

class LiveEventProcessor:
    def __init__(self, incrementer: IncrementalAnalyticsEngine):
        self.incrementer = incrementer

    async def process_event(self, session: LiveSession, event: Dict[str, Any]) -> LiveSession:
        """
        Receives dynamic telemetry notifications, computes rolling analytics,
        and pushes contextual coaching instructions to active WebSocket sessions.
        """
        event_type = event.get("event_type")
        round_number = event.get("round_number", 1)
        
        # 1. Resolve state for this round
        state = None
        for s in session.states:
            if s.round_number == round_number:
                state = s
                break
        if not state:
            state = SessionState(session_id=session.id, round_number=round_number)
            session.states.append(state)

        # 2. Process metrics
        if event_type == "KILL":
            state.kills += 1
        elif event_type == "DEATH":
            state.deaths += 1
        elif event_type == "ASSIST":
            state.assists += 1
        elif event_type == "BUY":
            state.credits = event.get("credits_remaining", 0)

        # 3. Predict rolling win probability and fatigue
        allies = event.get("allies_alive", 5)
        enemies = event.get("enemies_alive", 5)
        state.win_probability = self.incrementer.calculate_win_probability(
            allies_alive=allies,
            enemies_alive=enemies,
            credits_delta=state.credits - 3000
        )
        
        state.fatigue_index = self.incrementer.calculate_rolling_fatigue(
            round_num=round_number,
            recent_missed_shots=event.get("missed_shots", 0)
        )

        # 4. Dynamically generate alert recommendations
        recs = []
        if state.deaths > state.kills + 1:
            recs.append("Play for trades. Avoid isolated duels.")
        if state.credits < 2000 and event_type == "BUY":
            recs.append("Save credits. Keep economy stable for full buys.")
        if event_type == "SPIKE_PLANT" and allies < enemies:
            recs.append("Spike planted. Play safe post-plant crosshair angles.")
            
        state.recommendations = recs

        # 5. Broadcast to WebSocket overlay channel
        message = {
            "event": "COACHING_ALERT",
            "session_id": session.id,
            "round": round_number,
            "win_probability": state.win_probability,
            "fatigue_index": state.fatigue_index,
            "recommendations": state.recommendations,
            "meta": {
                "model_version": "1.0.0",
                "prompt_version": "1.0.0",
                "feature_version": "1.0.0"
            }
        }
        await ws_manager.send_personal_message(message, session.user_id)
        
        return session

from datetime import datetime, timezone
from typing import Callable, Dict, List, Type, Any, Optional
import structlog

logger = structlog.get_logger()

class Event:
    """Base event class containing universal event properties."""
    def __init__(self, timestamp: Optional[datetime] = None):
        self.timestamp = timestamp or datetime.now(timezone.utc)

class UserRegistered(Event):
    def __init__(self, user_id: str, email: str, timestamp: Optional[datetime] = None):
        super().__init__(timestamp)
        self.user_id = user_id
        self.email = email

class UserLoggedIn(Event):
    def __init__(self, user_id: str, email: str, timestamp: Optional[datetime] = None):
        super().__init__(timestamp)
        self.user_id = user_id
        self.email = email

class ProfileUpdated(Event):
    def __init__(self, user_id: str, updates: Dict[str, Any], timestamp: Optional[datetime] = None):
        super().__init__(timestamp)
        self.user_id = user_id
        self.updates = updates

class EventBus:
    def __init__(self):
        self._listeners: Dict[Any, List[Any]] = {}

    def subscribe(self, event_type: Any, listener: Any) -> None:
        """Register a handler for a specific event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)

    async def publish(self, event: Event) -> None:
        """Emit an event asynchronously to all registered listeners."""
        event_type = type(event)
        if event_type in self._listeners:
            for listener in self._listeners[event_type]:
                try:
                    await listener(event)
                except Exception as e:
                    logger.exception(
                        "Unhandled exception in event listener",
                        event=event_type.__name__,
                        error=str(e)
                    )

# Central Singleton Event Bus
event_bus = EventBus()

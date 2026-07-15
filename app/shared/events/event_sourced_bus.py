import structlog
import asyncio
from typing import Dict, Any, List, Callable, Coroutine
from app.shared.events.event_bus import Event

logger = structlog.get_logger()

class EventSourcedBus:
    def __init__(self):
        # Immutable event store registry
        self.event_store: List[Event] = []
        # Handlers map sorted by priority
        self.subscribers: Dict[type, List[Dict[str, Any]]] = {}
        # Dead Letter Queue for failed handlers
        self.dlq: List[Dict[str, Any]] = []

    def subscribe(
        self,
        event_type: type,
        handler: Callable[[Event], Coroutine[Any, Any, None]],
        priority: int = 10,
        retries: int = 3
    ) -> None:
        """Registers a handler to execute upon event emission with priority level."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append({
            "handler": handler,
            "priority": priority,
            "retries": retries
        })
        # Sort subscribers by priority descending (higher priority runs first)
        self.subscribers[event_type].sort(key=lambda x: x["priority"], reverse=True)

    async def publish(self, event: Event) -> None:
        """Emits an event, saving it to the store, and notifying all registered subscribers."""
        self.event_store.append(event)
        
        event_type = type(event)
        handlers = self.subscribers.get(event_type, [])
        
        for item in handlers:
            handler = item["handler"]
            max_retries = item["retries"]
            
            success = False
            for attempt in range(max_retries):
                try:
                    await handler(event)
                    success = True
                    break
                except Exception as e:
                    logger.error(
                        "Subscriber execution failed",
                        handler=handler.__name__,
                        attempt=attempt + 1,
                        error=str(e)
                    )
                    await asyncio.sleep(0.01)
                    
            if not success:
                logger.error(
                    "Subscriber failed all retries. Appending to DLQ.",
                    handler=handler.__name__,
                    event_type=event_type.__name__
                )
                self.dlq.append({
                    "event": event,
                    "handler_name": handler.__name__
                })

# Global Event Sourced Bus Instance
event_sourced_bus = EventSourcedBus()

import structlog
from typing import List, Callable, Dict, Any

logger = structlog.get_logger()

class SagaStep:
    def __init__(self, name: str, action: Callable[[Dict[str, Any]], Any], compensate: Callable[[Dict[str, Any]], Any]):
        self.name = name
        self.action = action
        self.compensate = compensate

class SagaCoordinator:
    def __init__(self):
        self.executed_steps: List[SagaStep] = []

    async def execute(self, steps: List[SagaStep], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes steps sequentially. If any step throws an exception,
        all executed steps are rolled back in reverse order.
        """
        logger.info("Starting Saga transaction execution")
        
        for step in steps:
            try:
                logger.info("Executing Saga step", step=step.name)
                # Execute action
                await step.action(context)
                self.executed_steps.append(step)
            except Exception as e:
                logger.error(
                    "Saga step failed. Initiating compensations.",
                    step=step.name,
                    error=str(e)
                )
                await self._compensate(context)
                raise e
                
        logger.info("Saga transaction completed successfully")
        return context

    async def _compensate(self, context: Dict[str, Any]) -> None:
        # Compensate in reverse order
        for step in reversed(self.executed_steps):
            try:
                logger.info("Compensating Saga step", step=step.name)
                await step.compensate(context)
            except Exception as e:
                logger.error(
                    "Compensation step failed during rollback",
                    step=step.name,
                    error=str(e)
                )

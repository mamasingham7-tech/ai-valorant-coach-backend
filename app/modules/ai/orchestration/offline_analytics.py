import structlog
import time
from typing import Dict, Any, List, Callable

logger = structlog.get_logger()

class DAGWorkflowEngine:
    def __init__(self):
        # Ordered list representing execution path (DAG linear sort)
        self.sequence: List[str] = []
        self.tasks: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}

    def add_task(self, name: str, func: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        self.tasks[name] = func
        self.sequence.append(name)

    async def execute_workflow(
        self,
        initial_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes the linear task path with retry overrides and execution checkpoints.
        """
        context = initial_context.copy()
        context["checkpoints"] = {}
        
        for task_name in self.sequence:
            func = self.tasks[task_name]
            retries = 3
            success = False
            
            while retries > 0 and not success:
                try:
                    logger.info("Executing DAG task", task_name=task_name)
                    context = func(context)
                    context["checkpoints"][task_name] = "COMPLETED"
                    success = True
                except Exception as e:
                    retries -= 1
                    logger.error(
                        "DAG task failed",
                        task_name=task_name,
                        retries_left=retries,
                        error=str(e)
                    )
                    if retries == 0:
                        context["checkpoints"][task_name] = "FAILED"
                        raise e
                    time.sleep(0.05)
                    
        return context

import re
import time
from typing import Dict, Any

class AISafetyLayer:
    @staticmethod
    def detect_prompt_injection(prompt: str) -> bool:
        """Flags phrases commonly used in LLM override attacks."""
        patterns = [
            r"ignore previous instructions",
            r"system override",
            r"forget all guidelines",
            r"you are now an administrator",
            r"bypass system configurations"
        ]
        for pattern in patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def sanitize_context(context: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively parses structures and redacts PII elements like email addresses."""
        email_pattern = r"[\w\.-]+@[\w\.-]+\.\w+"
        
        def mask_string(s: str) -> str:
            return re.sub(email_pattern, "[MASKED_EMAIL]", s)

        def traverse(data: Any) -> Any:
            if isinstance(data, dict):
                return {k: traverse(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [traverse(item) for item in data]
            elif isinstance(data, str):
                return mask_string(data)
            return data

        return traverse(context)

class CircuitBreakerOpenException(Exception):
    pass

class ProviderCircuitBreaker:
    """Prevents application lockups by failing fast if external APIs time out repeatedly."""
    def __init__(self, failure_threshold: int = 3, cooldown_seconds: int = 30):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.failures = 0
        self.last_failure_time = 0.0

    def record_success(self):
        self.failures = 0

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()

    def is_open(self) -> bool:
        if self.failures >= self.failure_threshold:
            if time.time() - self.last_failure_time < self.cooldown_seconds:
                return True
            else:
                self.failures = 0
        return False

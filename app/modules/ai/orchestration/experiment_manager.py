from typing import Dict, Any

class ExperimentManager:
    def __init__(self):
        # Maps experiment IDs to active variant splits
        self.experiments = {
            "exp-prompt-ab": {
                "name": "Coaching Style A/B Test",
                "variants": ["variant_A", "variant_B"],
                "split_ratio": 0.5
            }
        }

    def determine_variant(self, user_id: str, experiment_id: str) -> str:
        """
        Determines the test variant deterministically using user ID character sums.
        Guarantees that a user always receives the same variant for an experiment.
        """
        if experiment_id not in self.experiments:
            return "control"
            
        config = self.experiments[experiment_id]
        char_sum = sum(ord(c) for c in user_id)
        index = char_sum % len(config["variants"])
        return config["variants"][index]

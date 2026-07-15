import numpy as np
from typing import Dict

class ThompsonBanditOptimizer:
    def __init__(self):
        # Alpha (successes) and Beta (failures) parameters for Thompson Sampling
        self.priors: Dict[str, Dict[str, float]] = {
            "burst-drill": {"alpha": 2.0, "beta": 2.0},
            "strafe-drill": {"alpha": 2.0, "beta": 2.0},
            "rotation-drill": {"alpha": 2.0, "beta": 2.0},
            "eco-drill": {"alpha": 2.0, "beta": 2.0}
        }

    def sample_best_drill(self, user_category: str) -> str:
        """Selects the optimal practice drill via beta distribution sampling."""
        sampled_vals = {}
        for drill, params in self.priors.items():
            # Beta distribution sampling
            sampled_vals[drill] = np.random.beta(params["alpha"], params["beta"])
            
        best_drill = max(sampled_vals, key=sampled_vals.get)
        return best_drill

    def update_priors(self, drill_id: str, success: bool) -> None:
        """Adjusts alpha/beta parameters based on reinforcement feedback reward loops."""
        if drill_id in self.priors:
            if success:
                self.priors[drill_id]["alpha"] += 1.0
            else:
                self.priors[drill_id]["beta"] += 1.0

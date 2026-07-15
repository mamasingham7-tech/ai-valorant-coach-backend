import numpy as np
import structlog
from typing import Dict

logger = structlog.get_logger()

class PrivacyPreservingEngine:
    def inject_noise_to_weights(
        self,
        weights: Dict[str, float],
        epsilon: float,
        sensitivity: float = 1.0
    ) -> Dict[str, float]:
        """
        Applies Differential Privacy by adding Laplacian noise to weights parameters.
        Scale parameter is defined as sensitivity / epsilon.
        """
        if epsilon <= 0:
            epsilon = 1.0
            
        scale = sensitivity / epsilon
        noised_weights = {}
        for key, val in weights.items():
            noise = np.random.laplace(0.0, scale)
            noised_weights[key] = val + noise
            
        logger.info("Laplacian noise injected to local weights parameters", epsilon=epsilon)
        return noised_weights

    def clip_gradients(self, weights: Dict[str, float], max_norm: float = 1.0) -> Dict[str, float]:
        """Clips parameter values to satisfy maximum norm sensitivity boundaries."""
        clipped = {}
        for key, val in weights.items():
            clipped[key] = max(-max_norm, min(max_norm, val))
        return clipped

from dataclasses import dataclass
from datetime import datetime

@dataclass
class ModelLineage:
    """Tracks prompt version, provider, and deployment environment dependencies for models."""
    training_source: str
    prompt_version: str
    feature_version: str
    analytics_version: str
    provider: str
    deployment_environment: str

@dataclass
class ModelRegistryEntry:
    """Stores version metadata registry listings for active models."""
    name: str
    version: str
    status: str
    release_date: datetime
    owner: str
    description: str
    rollback_version: str
    lineage: ModelLineage

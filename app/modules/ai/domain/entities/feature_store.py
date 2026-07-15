from dataclasses import dataclass, field
from datetime import datetime
from typing import List

@dataclass
class FeatureLineage:
    """Tracks lineage transformations and original telemetry dependencies for audits."""
    raw_telemetry_source: str
    transformation_pipeline: str
    dependencies: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class FeatureStoreEntry:
    """Stores calculated performance metrics directly to avoid duplicate processing."""
    feature_name: str
    feature_value: float
    feature_version: str
    calculation_method: str
    sample_size: int
    confidence: float
    lineage: FeatureLineage

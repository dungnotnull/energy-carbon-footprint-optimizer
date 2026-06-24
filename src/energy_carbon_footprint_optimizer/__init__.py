'''energy_carbon_footprint_optimizer — production-grade carbon accounting & decarbonisation harness.'''

__version__ = "0.1.0"

from .harness import run_harness
from .models import (
    ComplianceResult,
    DimensionScore,
    EmissionScope,
    EnergyMetrics,
    EntityType,
    EvaluationReport,
    EvidenceSource,
    EvidenceTier,
    FrameworkApplication,
    Impact,
    Effort,
    RoadmapItem,
    ScoringInput,
    Target,
)

__all__ = [
    "run_harness",
    "ComplianceResult",
    "DimensionScore",
    "EmissionScope",
    "EnergyMetrics",
    "EntityType",
    "EvaluationReport",
    "EvidenceSource",
    "EvidenceTier",
    "FrameworkApplication",
    "Impact",
    "Effort",
    "RoadmapItem",
    "ScoringInput",
    "Target",
]

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field
from .constants import EntityType, EvidenceTier, Impact, Effort


class EmissionScope(BaseModel):
    co2_kg: Optional[float] = None
    description: str = ""
    source: str = ""
    verified: bool = False


class EnergyMetrics(BaseModel):
    annual_kwh: Optional[float] = None
    area_m2: Optional[float] = None
    employees: Optional[int] = None
    revenue_k: Optional[float] = None
    renewable_share: float = Field(0.0, ge=0.0, le=1.0)
    efficiency_measures: List[str] = Field(default_factory=list)
    energy_intensity_unit: str = ""


class Target(BaseModel):
    description: str
    year: Optional[int] = None
    sbti_validated: bool = False
    net_zero: bool = False
    coverage_percent: float = Field(0.0, ge=0.0, le=100.0)


class EvidenceSource(BaseModel):
    title: str
    url: str = ""
    year: Optional[int] = None
    tier: EvidenceTier = EvidenceTier.FRAMEWORK_DOC
    finding: str = ""


class FrameworkApplication(BaseModel):
    framework_id: str
    name: str
    reason: str
    scopes: List[str] = Field(default_factory=list)


class DimensionScore(BaseModel):
    dimension: str
    score: float = Field(..., ge=0.0, le=5.0)
    weight: float = Field(..., ge=0.0, le=1.0)
    evidence: str
    justification: str
    source: Optional[str] = None
    evidence_tier: str = ""


class RoadmapItem(BaseModel):
    rank: int = 0
    recommendation: str
    impact: Impact
    effort: Effort
    cost_level: str = ""
    framework_basis: str
    emissions_reduction_kg: Optional[float] = None
    payback_years: Optional[float] = None
    category: str


class ChallengeNote(BaseModel):
    counter_argument: str
    affected_dimension: str
    original_score: float
    revised_score: float
    rationale: str


class ComplianceResult(BaseModel):
    passed: bool
    blocking_issues: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    disclaimers: List[str] = Field(default_factory=list)


class ScoringInput(BaseModel):
    entity_type: EntityType
    name: str = ""
    region: str = ""
    scope1: EmissionScope = Field(default_factory=EmissionScope)
    scope2: EmissionScope = Field(default_factory=EmissionScope)
    scope3: EmissionScope = Field(default_factory=EmissionScope)
    energy: EnergyMetrics = Field(default_factory=EnergyMetrics)
    targets: List[Target] = Field(default_factory=list)
    claims: List[str] = Field(default_factory=list)
    evidence: List[EvidenceSource] = Field(default_factory=list)
    research_degraded: bool = False


class EvaluationReport(BaseModel):
    overall_score: float
    scoring_table: List[DimensionScore]
    challenge_notes: List[ChallengeNote]
    roadmap: List[RoadmapItem]
    compliance: ComplianceResult
    sources: List[EvidenceSource]
    degraded_mode: bool
    executive_summary: str = ""
    frameworks: List[FrameworkApplication] = Field(default_factory=list)

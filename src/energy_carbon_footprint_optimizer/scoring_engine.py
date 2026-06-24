from typing import List, Optional, Tuple
from .constants import (
    BENCHMARKS,
    DEFAULT_WEIGHTS,
    DIMENSIONS,
    EntityType,
    EvidenceTier,
)
from .models import DimensionScore, EmissionScope, EnergyMetrics, FrameworkApplication, ScoringInput, Target


def _performance_score(actual: float, benchmark: float) -> float:
    '''Return a 0–5 score where lower actual emissions/intensity is better.'''
    if benchmark <= 0:
        return 0.0
    ratio = actual / benchmark
    # 0.5×benchmark = 5, benchmark = 2.5, 2×benchmark = 0
    score = 5.0 - 2.5 * ratio
    return max(0.0, min(5.0, score))


def _completeness(scope: EmissionScope) -> float:
    if scope.co2_kg is None:
        return 0.0
    return 5.0 if scope.verified else 2.5


def _format_source(evidence: List, degraded: bool) -> Tuple[str, str]:
    if evidence:
        src = evidence[0]
        return src.title, src.tier.value
    if degraded:
        return "SECOND-KNOWLEDGE-BRAIN.md fallback", EvidenceTier.KNOWLEDGE_BRAIN.value
    return "Framework default / no external evidence", EvidenceTier.FRAMEWORK_DOC.value


def _score_scope(
    scope: EmissionScope,
    benchmark_value: float,
    dimension: str,
    evidence_title: str,
    evidence_tier: str,
) -> DimensionScore:
    completeness = _completeness(scope)
    if scope.co2_kg is not None and benchmark_value > 0:
        perf = _performance_score(scope.co2_kg, benchmark_value)
        score = 0.4 * completeness + 0.6 * perf
    else:
        score = completeness
        perf = 0.0

    score = round(max(0.0, min(5.0, score)), 2)

    if scope.co2_kg is None:
        justification = "No emission data provided; score reflects data completeness only."
    else:
        justification = (
            f"{scope.co2_kg:.0f} kgCO2e vs benchmark {benchmark_value:.0f}; "
            f"performance {perf:.1f}/5, completeness {completeness:.1f}/5."
        )

    return DimensionScore(
        dimension=dimension,
        score=score,
        weight=DEFAULT_WEIGHTS[dimension],
        evidence=f"{evidence_tier}: {evidence_title}",
        justification=justification,
        evidence_tier=evidence_tier,
        source=scope.source,
    )


def _energy_intensity(energy: EnergyMetrics) -> Tuple[Optional[float], str]:
    if energy.annual_kwh is None or energy.annual_kwh <= 0:
        return None, ""
    if energy.area_m2 and energy.area_m2 > 0:
        return energy.annual_kwh / energy.area_m2, "kWh/m²/year"
    if energy.employees and energy.employees > 0:
        return energy.annual_kwh / float(energy.employees), "kWh/employee/year"
    return None, ""


def _score_energy_efficiency(
    energy: EnergyMetrics,
    benchmarks: dict,
    evidence_title: str,
    evidence_tier: str,
) -> DimensionScore:
    intensity, unit = _energy_intensity(energy)
    bench_value = benchmarks.get("energy_intensity", {}).get("value", 0.0)

    if intensity is not None and bench_value > 0:
        completeness = 5.0
        perf = _performance_score(intensity, bench_value)
    elif energy.annual_kwh is not None:
        completeness = 3.0
        perf = 0.0
    else:
        completeness = 0.0
        perf = 0.0

    measure_bonus = 0.25 * len(energy.efficiency_measures)
    score = min(5.0, 0.4 * completeness + 0.6 * perf + measure_bonus)
    score = round(score, 2)

    if intensity is not None:
        justification = (
            f"Energy intensity {intensity:.1f} {unit} vs benchmark {bench_value:.1f}; "
            f"efficiency measures: {len(energy.efficiency_measures)}."
        )
    elif energy.annual_kwh is not None:
        justification = (
            f"Annual {energy.annual_kwh:.0f} kWh provided but no normaliser (area/employees); "
            f"scoring based on completeness and {len(energy.efficiency_measures)} measures."
        )
    else:
        justification = "No energy data provided; score reflects missing data."

    return DimensionScore(
        dimension="Energy-efficiency level",
        score=score,
        weight=DEFAULT_WEIGHTS["Energy-efficiency level"],
        evidence=f"{evidence_tier}: {evidence_title}",
        justification=justification,
        evidence_tier=evidence_tier,
        source="ISO 50001 / energy hierarchy",
    )


def _score_renewables(
    energy: EnergyMetrics,
    evidence_title: str,
    evidence_tier: str,
) -> DimensionScore:
    base = 5.0 * energy.renewable_share
    substitutions = [
        m
        for m in energy.efficiency_measures
        if any(k in m.lower() for k in ("electrify", "ev", "heat pump", "green supplier", "ppa", "rec"))
    ]
    bonus = 0.5 * len(substitutions)
    score = min(5.0, base + bonus)
    score = round(score, 2)

    justification = (
        f"Renewable share {energy.renewable_share:.0%} ({base:.1f}/5) plus "
        f"{len(substitutions)} substitution measures."
    )

    return DimensionScore(
        dimension="Renewables & substitution",
        score=score,
        weight=DEFAULT_WEIGHTS["Renewables & substitution"],
        evidence=f"{evidence_tier}: {evidence_title}",
        justification=justification,
        evidence_tier=evidence_tier,
        source="GHG Protocol Scope 2 / energy hierarchy",
    )


def _score_targets(
    targets: List[Target],
    evidence_title: str,
    evidence_tier: str,
) -> DimensionScore:
    if not targets:
        score = 0.0
        justification = "No reduction target documented; credibility is zero."
    else:
        t = max(targets, key=lambda x: (x.sbti_validated, x.net_zero, x.coverage_percent))
        score = 1.0
        if t.year and t.year <= 2030:
            score += 0.5
        if t.sbti_validated:
            score += 1.5
        if t.net_zero:
            score += 1.0
        if t.coverage_percent >= 66:
            score += 1.0
        score = min(5.0, score)
        score = round(score, 2)
        justification = (
            f"Target '{t.description}' — SBTi validated: {t.sbti_validated}, "
            f"net-zero: {t.net_zero}, coverage: {t.coverage_percent:.0f}%, year: {t.year}."
        )

    return DimensionScore(
        dimension="Reduction-target credibility (SBTi)",
        score=score,
        weight=DEFAULT_WEIGHTS["Reduction-target credibility (SBTi)"],
        evidence=f"{evidence_tier}: {evidence_title}",
        justification=justification,
        evidence_tier=evidence_tier,
        source="SBTi Corporate Net-Zero Standard",
    )


def score_dimensions(
    inp: ScoringInput,
    frameworks: List[FrameworkApplication],
) -> List[DimensionScore]:
    '''Score all six dimensions for the given input.'''
    benchmarks = BENCHMARKS.get(inp.entity_type, BENCHMARKS[EntityType.OTHER])
    evidence_title, evidence_tier = _format_source(inp.evidence, inp.research_degraded)

    scores = [
        _score_scope(
            inp.scope1,
            benchmarks["scope1"]["value"],
            "Scope 1 direct emissions",
            evidence_title,
            evidence_tier,
        ),
        _score_scope(
            inp.scope2,
            benchmarks["scope2"]["value"],
            "Scope 2 energy emissions",
            evidence_title,
            evidence_tier,
        ),
        _score_scope(
            inp.scope3,
            benchmarks["scope3"]["value"],
            "Scope 3 value-chain emissions",
            evidence_title,
            evidence_tier,
        ),
        _score_energy_efficiency(
            inp.energy,
            benchmarks,
            evidence_title,
            evidence_tier,
        ),
        _score_renewables(
            inp.energy,
            evidence_title,
            evidence_tier,
        ),
        _score_targets(
            inp.targets,
            evidence_title,
            evidence_tier,
        ),
    ]

    # Defensive: ensure every dimension exists exactly once.
    assert [s.dimension for s in scores] == DIMENSIONS
    return scores


def overall_score(scores: List[DimensionScore]) -> float:
    total = sum(s.score * s.weight for s in scores)
    weight = sum(s.weight for s in scores)
    if weight == 0:
        return 0.0
    return round(total / weight, 2)

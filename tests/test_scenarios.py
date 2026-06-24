'''End-to-end scenario tests for energy_carbon_footprint_optimizer.'''
import pytest

from energy_carbon_footprint_optimizer.constants import DIMENSIONS, EntityType, EvidenceTier
from energy_carbon_footprint_optimizer.harness import (
    ComplianceBlockedError,
    IntakeIncompleteError,
    run_harness,
)
from energy_carbon_footprint_optimizer.models import (
    EmissionScope,
    EnergyMetrics,
    EvaluationReport,
    EvidenceSource,
    RoadmapItem,
    ScoringInput,
    Target,
)


def _evidence():
    return EvidenceSource(
        title="GHG Protocol Corporate Standard",
        url="https://ghgprotocol.org/corporate-standard",
        year=2015,
        tier=EvidenceTier.FRAMEWORK_DOC,
        finding="Scope 1/2/3 accounting baseline",
    )


def test_scenario_1_happy_path_full_audit():
    inp = ScoringInput(
        entity_type=EntityType.SME,
        name="GreenTech Ltd",
        region="EU",
        scope1=EmissionScope(co2_kg=2400, description="natural gas & fleet", verified=True),
        scope2=EmissionScope(co2_kg=2000, description="purchased electricity", verified=True),
        scope3=EmissionScope(co2_kg=4500, description="business travel & suppliers", verified=False),
        energy=EnergyMetrics(
            annual_kwh=7000,
            employees=3,
            renewable_share=0.2,
            efficiency_measures=["LED lighting", "smart thermostats"],
        ),
        targets=[
            Target(
                description="50% reduction by 2030",
                year=2030,
                sbti_validated=True,
                coverage_percent=80,
            )
        ],
        evidence=[_evidence()],
    )
    report = run_harness(inp)
    assert isinstance(report, EvaluationReport)
    assert len(report.scoring_table) == 6
    assert report.compliance.passed
    assert len(report.roadmap) >= 3
    assert len(report.challenge_notes) >= 3
    assert 0 <= report.overall_score <= 5
    assert all(d.impact and d.effort for d in report.roadmap)
    assert any("Energy hierarchy" in r.framework_basis or "MACC" in r.framework_basis for r in report.roadmap)


def test_scenario_2_ambiguous_input():
    inp = ScoringInput(
        entity_type=EntityType.SME,
        name="",
        region="",
        scope1=EmissionScope(),
        scope2=EmissionScope(),
        scope3=EmissionScope(),
        energy=EnergyMetrics(),
    )
    with pytest.raises(IntakeIncompleteError) as exc:
        run_harness(inp)
    assert 1 <= len(exc.value.questions) <= 5
    assert any("employees" in q.lower() for q in exc.value.questions)


def test_scenario_3_offline_degraded_mode():
    inp = ScoringInput(
        entity_type=EntityType.HOUSEHOLD,
        name="My home",
        region="",
        energy=EnergyMetrics(annual_kwh=4500, area_m2=120, renewable_share=0.1),
        research_degraded=True,
    )
    report = run_harness(inp)
    assert isinstance(report, EvaluationReport)
    assert report.degraded_mode
    assert "fallback" in report.executive_summary.lower()


def test_scenario_4_challenge_changes_verdict():
    inp = ScoringInput(
        entity_type=EntityType.HOUSEHOLD,
        name="Optimistic household",
        region="",
        energy=EnergyMetrics(annual_kwh=3000, area_m2=100, renewable_share=0.9),
        scope3=EmissionScope(co2_kg=1000, description="consumption", verified=False),
        targets=[
            Target(
                description="Net-zero by 2030",
                year=2030,
                sbti_validated=False,
                coverage_percent=100,
                net_zero=True,
            )
        ],
        evidence=[EvidenceSource(title="Blog post", tier=EvidenceTier.BLOG)],
    )
    report = run_harness(inp)
    assert any(note.revised_score < note.original_score for note in report.challenge_notes)
    # Energy-efficiency score should be revised because it lacked normalisation evidence.
    energy_score = next(
        d.score for d in report.scoring_table if d.dimension == "Energy-efficiency level"
    )
    assert energy_score < 4.5


def test_scenario_5_roadmap_only():
    inp = ScoringInput(
        entity_type=EntityType.HOUSEHOLD,
        name="Simple home",
        region="",
        energy=EnergyMetrics(annual_kwh=5000, area_m2=120, renewable_share=0.2),
    )
    result = run_harness(inp, mode="roadmap_only")
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(r, RoadmapItem) for r in result)
    assert all(r.impact and r.effort for r in result)
    ranks = [r.rank for r in result]
    assert ranks == sorted(ranks)


def test_scenario_6_compliance_gate_block():
    inp = ScoringInput(
        entity_type=EntityType.SME,
        name="Greenwash Corp",
        region="EU",
        scope1=EmissionScope(co2_kg=10000, verified=False),
        scope2=EmissionScope(co2_kg=8000, verified=False),
        scope3=EmissionScope(co2_kg=5000, verified=False),
        energy=EnergyMetrics(annual_kwh=20000, employees=5, renewable_share=0.0),
        claims=["Carbon neutral today", "100% offset"],
        evidence=[_evidence()],
    )
    with pytest.raises(ComplianceBlockedError) as exc:
        run_harness(inp)
    issues = " ".join(exc.value.issues).lower()
    assert "carbon-neutral" in issues or "net-zero" in issues or "sbti" in issues


def test_regression_all_dimensions_present():
    inp = ScoringInput(
        entity_type=EntityType.HOUSEHOLD,
        name="Regression home",
        region="",
        energy=EnergyMetrics(annual_kwh=4000, area_m2=100, renewable_share=0.3),
    )
    report = run_harness(inp)
    names = [d.dimension for d in report.scoring_table]
    assert sorted(names) == sorted(DIMENSIONS)


def test_regression_named_framework_cited():
    inp = ScoringInput(
        entity_type=EntityType.SME,
        name="Framework SME",
        region="UK",
        energy=EnergyMetrics(annual_kwh=5000, employees=2, renewable_share=0.0),
        evidence=[_evidence()],
    )
    report = run_harness(inp)
    ids = {f.framework_id for f in report.frameworks}
    assert "ghg-protocol" in ids
    assert "iso-14064-50001" in ids


def test_regression_evidence_tiers_labelled():
    inp = ScoringInput(
        entity_type=EntityType.INDIVIDUAL,
        name="Evidence person",
        region="",
        energy=EnergyMetrics(annual_kwh=2000, renewable_share=0.1),
        evidence=[_evidence()],
    )
    report = run_harness(inp)
    for dim in report.scoring_table:
        assert dim.evidence
        assert any(
            tier in dim.evidence
            for tier in ["Framework / Standard document", "SECOND-KNOWLEDGE-BRAIN fallback"]
        )


def test_regression_compliance_before_output():
    inp = ScoringInput(
        entity_type=EntityType.SME,
        name="Compliance SME",
        region="US",
        claims=["Carbon neutral"],
        scope1=EmissionScope(co2_kg=1000, verified=False),
        energy=EnergyMetrics(annual_kwh=5000, employees=2, renewable_share=0.0),
    )
    with pytest.raises(ComplianceBlockedError):
        run_harness(inp)


def test_regression_roadmap_ranked_by_impact_effort():
    inp = ScoringInput(
        entity_type=EntityType.HOUSEHOLD,
        name="Rank home",
        region="",
        energy=EnergyMetrics(annual_kwh=4000, area_m2=100, renewable_share=0.2),
    )
    roadmap = run_harness(inp, mode="roadmap_only")
    # First item should have high impact and low effort, and be a 'reduce' action.
    first = roadmap[0]
    assert first.impact.value == "H"
    assert first.effort.value in ("L", "M")
    assert first.category == "reduce"

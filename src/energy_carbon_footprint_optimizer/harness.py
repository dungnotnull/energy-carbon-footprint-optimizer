from typing import List, Union
from .constants import DIMENSIONS, EntityType, EvidenceTier
from .compliance_check import run_compliance
from .framework_selector import select_frameworks
from .improvement_roadmap import build_roadmap
from .knowledge_brain import load_brain_sources
from .models import (
    ChallengeNote,
    ComplianceResult,
    DimensionScore,
    EvaluationReport,
    FrameworkApplication,
    RoadmapItem,
    ScoringInput,
)
from .scoring_engine import overall_score, score_dimensions


class IntakeIncompleteError(Exception):
    def __init__(self, questions: List[str]):
        self.questions = questions
        super().__init__(f"Intake incomplete; missing answers: {questions}")


class QualityGateError(Exception):
    pass


class ComplianceBlockedError(Exception):
    def __init__(self, issues: List[str]):
        self.issues = issues
        super().__init__(f"Compliance gate blocked: {issues}")


def _intake_check(inp: ScoringInput) -> None:
    questions: List[str] = []
    if not inp.name:
        questions.append("What is the name or identifier of the subject?")
    if inp.entity_type == EntityType.HOUSEHOLD and (not inp.energy.area_m2 or inp.energy.area_m2 <= 0):
        questions.append("What is the floor area (mÂ²) of the household?")
    if inp.entity_type == EntityType.SME and (not inp.energy.employees or inp.energy.employees <= 0):
        questions.append("How many employees does the SME have?")
    if all(s.co2_kg is None for s in (inp.scope1, inp.scope2, inp.scope3)) and inp.energy.annual_kwh is None:
        questions.append(
            "Please provide at least one Scope 1/2/3 emission value or an annual energy consumption figure."
        )
    if questions:
        raise IntakeIncompleteError(questions[:5])


def _challenge_phase(scores: List[DimensionScore], inp: ScoringInput) -> List[ChallengeNote]:
    by_name = {s.dimension: s for s in scores}
    notes: List[ChallengeNote] = []
    weak_tiers = {
        EvidenceTier.BLOG.value,
        EvidenceTier.EXPERT_OPINION.value,
        EvidenceTier.KNOWLEDGE_BRAIN.value,
    }

    # Counter-argument 1: Scope 3 underreporting when unverified.
    scope3 = by_name.get("Scope 3 value-chain emissions")
    if scope3 and scope3.score >= 3.5 and not inp.scope3.verified:
        revised = max(0.0, scope3.score - 0.5)
        notes.append(
            ChallengeNote(
                counter_argument="Scope 3 data are often incomplete; suppliers may not report upstream emissions.",
                affected_dimension="Scope 3 value-chain emissions",
                original_score=scope3.score,
                revised_score=revised,
                rationale="Penalty applied because Scope 3 data is unverified and likely underestimated.",
            )
        )

    # Counter-argument 2: high scores resting on weak evidence are marked down.
    for s in scores:
        if s.score >= 4.0 and s.evidence_tier in weak_tiers:
            if any(n.affected_dimension == s.dimension for n in notes):
                continue
            revised = max(0.0, s.score - 0.5)
            notes.append(
                ChallengeNote(
                    counter_argument=f"{s.dimension} score is high but rests on weak evidence ({s.evidence_tier}); independent verification is needed.",
                    affected_dimension=s.dimension,
                    original_score=s.score,
                    revised_score=revised,
                    rationale="Penalty applied because a high score is supported by blog, opinion or fallback evidence rather than authoritative data.",
                )
            )

    # Counter-argument 3: net-zero / offset dependency.
    claims_text = " ".join(c.lower() for c in inp.claims)
    if any(k in claims_text for k in ("net-zero", "net zero", "carbon neutral", "offset")):
        target_dim = by_name.get("Reduction-target credibility (SBTi)")
        if target_dim and not any(n.affected_dimension == target_dim.dimension for n in notes):
            revised = max(0.0, target_dim.score - 0.5)
            notes.append(
                ChallengeNote(
                    counter_argument="Net-zero or carbon-neutral claims that rely heavily on offsets rather than abatement are high-risk.",
                    affected_dimension="Reduction-target credibility (SBTi)",
                    original_score=target_dim.score,
                    revised_score=revised,
                    rationale="Penalty applied because offset/neutrality claims require stronger abatement evidence.",
                )
            )

    # Generic fallback counter-arguments guarantee at least three are documented.
    generic_counterarguments = [
        ("Scope 1 direct emissions", "Fugitive, process and non-CO2 emissions are frequently underestimated in self-reported Scope 1 data."),
        ("Scope 2 energy emissions", "Location-based vs market-based accounting can materially change Scope 2 results; market-based claims need contractual instruments."),
        ("Scope 3 value-chain emissions", "Scope 3 categories are broad and depend on supplier data quality; omissions are common."),
        ("Energy-efficiency level", "Efficiency benchmarks vary by sector and climate zone; cross-sector comparisons may overstate performance."),
        ("Renewables & substitution", "Renewable electricity claims require additionality and time-matching to avoid greenwashing."),
        ("Reduction-target credibility (SBTi)", "Targets need independent validation and annual progress disclosure to remain credible."),
    ]
    for dim, argument in generic_counterarguments:
        if len(notes) >= 3:
            break
        if any(n.affected_dimension == dim for n in notes):
            continue
        s = by_name.get(dim)
        original = s.score if s else 0.0
        notes.append(
            ChallengeNote(
                counter_argument=argument,
                affected_dimension=dim,
                original_score=original,
                revised_score=original,
                rationale="Documented for completeness; no score change because no specific risk flag was triggered.",
            )
        )

    return notes

def _apply_challenge(
    scores: List[DimensionScore], notes: List[ChallengeNote]
) -> List[DimensionScore]:
    by_name = {s.dimension: s for s in scores}
    for note in notes:
        s = by_name.get(note.affected_dimension)
        if s:
            s.score = round(max(0.0, min(5.0, note.revised_score)), 2)
    return list(by_name.values())


def _synthesize(
    scores: List[DimensionScore],
    roadmap: List[RoadmapItem],
    challenge_notes: List[ChallengeNote],
    compliance: ComplianceResult,
    frameworks: List[FrameworkApplication],
    sources: list,
    degraded: bool,
) -> EvaluationReport:
    overall = overall_score(scores)
    sorted_scores = sorted(scores, key=lambda x: x.score, reverse=True)
    strengths = [s.dimension for s in sorted_scores[:3]]
    priorities = [r.recommendation for r in roadmap[:3]]

    summary_parts = [f"Overall score: {overall:.2f} / 5"]
    if degraded:
        summary_parts.append("Research tools were unavailable; SECOND-KNOWLEDGE-BRAIN fallback applied.")
    summary_parts.append(f"Top strengths: {', '.join(strengths)}")
    summary_parts.append(f"Top priorities: {', '.join(priorities)}")

    return EvaluationReport(
        overall_score=overall,
        scoring_table=scores,
        challenge_notes=challenge_notes,
        roadmap=roadmap,
        compliance=compliance,
        sources=sources,
        degraded_mode=degraded,
        executive_summary=" ".join(summary_parts),
        frameworks=frameworks,
    )


def _quality_gate_check(report: EvaluationReport) -> None:
    if len(report.scoring_table) != 6:
        raise QualityGateError("All 6 dimensions must be scored before output.")
    if not all(d.evidence for d in report.scoring_table):
        raise QualityGateError("Every dimension must cite a source or a fallback label.")
    if not report.frameworks:
        raise QualityGateError("At least one named framework must be explicitly applied.")
    if len(report.challenge_notes) < 3:
        raise QualityGateError("Challenge phase must document at least 3 counter-arguments.")
    if not report.compliance.passed:
        raise QualityGateError("Compliance gate must pass before output.")
    if not report.roadmap:
        raise QualityGateError("Roadmap must contain at least one item.")
    if not all(r.impact and r.effort for r in report.roadmap):
        raise QualityGateError("Every roadmap item must have impact and effort ratings.")
    if report.degraded_mode and not any(
        "fallback" in d.evidence.lower() or "SECOND-KNOWLEDGE-BRAIN" in d.evidence
        for d in report.scoring_table
    ):
        raise QualityGateError("Degraded mode must be labelled in the report.")


def run_harness(
    inp: ScoringInput, mode: str = "full"
) -> Union[EvaluationReport, List[RoadmapItem]]:
    '''Run the full energy/carbon footprint evaluation harness.'''
    if mode not in {"full", "roadmap_only"}:
        raise ValueError("mode must be 'full' or 'roadmap_only'")

    _intake_check(inp)

    frameworks = select_frameworks(inp.entity_type, inp.claims)
    if not frameworks:
        raise QualityGateError("No applicable framework was selected.")

    degraded = inp.research_degraded or not inp.evidence
    if degraded:
        inp.research_degraded = True
    sources = list(inp.evidence) if inp.evidence else load_brain_sources()[:5]

    scores = score_dimensions(inp, frameworks)
    if {s.dimension for s in scores} != set(DIMENSIONS):
        raise QualityGateError("Scoring engine produced an incomplete dimension set.")

    roadmap = build_roadmap(inp, scores)
    challenge_notes = _challenge_phase(scores, inp)
    revised_scores = _apply_challenge(scores, challenge_notes)

    compliance = run_compliance(inp, revised_scores, frameworks)
    if not compliance.passed:
        raise ComplianceBlockedError(compliance.blocking_issues)

    if mode == "roadmap_only":
        return roadmap

    report = _synthesize(
        revised_scores,
        roadmap,
        challenge_notes,
        compliance,
        frameworks,
        sources,
        degraded,
    )
    _quality_gate_check(report)
    return report



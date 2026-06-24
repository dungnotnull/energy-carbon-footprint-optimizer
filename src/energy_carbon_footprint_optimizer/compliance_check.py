from typing import List
from .constants import EntityType
from .models import ComplianceResult, DimensionScore, FrameworkApplication, ScoringInput


def run_compliance(
    inp: ScoringInput,
    dimension_scores: List[DimensionScore],
    frameworks: List[FrameworkApplication],
) -> ComplianceResult:
    '''Validate the deliverable against GHG Protocol / SBTi anti-greenwashing rules.'''
    blocking: List[str] = []
    warnings: List[str] = []
    disclaimers: List[str] = []

    claims_text = " ".join(c.lower() for c in inp.claims)
    has_net_zero_claim = any(k in claims_text for k in ("net-zero", "net zero", "carbon neutral", "climate neutral"))
    has_offset_claim = "offset" in claims_text
    has_sbti_target = any(t.sbti_validated for t in inp.targets)
    has_net_zero_target = any(t.net_zero for t in inp.targets)

    # 1. Greenwashing gate: net-zero / carbon-neutral claims need a validated target and abatement plan.
    if has_net_zero_claim:
        if not has_sbti_target:
            blocking.append(
                "Net-zero / carbon-neutral claim requires an SBTi-validated (or equivalent science-based) target."
            )
        if not has_net_zero_target:
            blocking.append(
                "Net-zero / carbon-neutral claim must be backed by a documented net-zero target year and pathway."
            )
        if has_offset_claim and not has_net_zero_target:
            blocking.append(
                "Offset-based neutrality claims may only cover residual emissions after science-based abatement."
            )

    # 2. Scope 3 materiality warning.
    total = sum((s.co2_kg or 0) for s in (inp.scope1, inp.scope2, inp.scope3))
    scope3_share = (inp.scope3.co2_kg or 0) / total if total else 0.0
    if scope3_share > 0.4:
        warnings.append(
            "Scope 3 is material (>40% of total). Disclose categories and methodology per GHG Protocol Scope 3 Standard."
        )

    # 3. High score without verification warning.
    unverified_high = any(
        d.score >= 4.0
        and d.evidence == "Framework default / no external evidence"
        for d in dimension_scores
    )
    if unverified_high:
        warnings.append(
            "One or more high scores rely on self-reported data only; independent verification is recommended."
        )

    # 4. SME/Other: ISO 14064/50001 disclaimer if not explicitly applied.
    if inp.entity_type in {EntityType.SME, EntityType.OTHER}:
        applied = {f.framework_id for f in frameworks}
        if "iso-14064-50001" not in applied:
            warnings.append(
                "For organisations, ISO 14064/50001-aligned quantification and energy management is recommended."
            )

    # 5. Required disclaimers.
    disclaimers.append(
        "This evaluation is educational and is not a substitute for professional carbon accounting, legal, or regulatory advice."
    )
    regulated_regions = {"eu", "uk", "ca", "us", "au", "gb", "de", "fr"}
    region = inp.region.lower().strip()
    if any(r in region for r in regulated_regions):
        disclaimers.append(
            f"Regulated reporting or disclosure requirements may apply in {inp.region}; consult a qualified local expert."
        )

    return ComplianceResult(
        passed=len(blocking) == 0,
        blocking_issues=blocking,
        warnings=warnings,
        disclaimers=disclaimers,
    )
